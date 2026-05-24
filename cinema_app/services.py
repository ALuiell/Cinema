import json
import locale
import logging

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.urls import reverse

from .models import Movie, Order, Ticket

try:
    import stripe
except ImportError:  # pragma: no cover - optional dependency for local study setup
    stripe = None

if stripe is not None:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe.api_version = settings.STRIPE_API_VERSION


logger = logging.getLogger(__name__)


def get_movies_list(queryset, genre_ids, age_limit, search_query):
    if genre_ids:
        valid_genres = [genre for genre in genre_ids if genre.isdigit()]
        if valid_genres:
            queryset = queryset.filter(genre__id__in=valid_genres).distinct()

    if age_limit and age_limit.isdigit():
        queryset = queryset.filter(age_limit=int(age_limit))

    if search_query:
        search_query = search_query.capitalize()
        query = (
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(original_name__icontains=search_query)
        )
        queryset = queryset.filter(query)

    return queryset


def get_sessions_list(queryset, movie_slug, session_date):
    if movie_slug:
        queryset = queryset.filter(movie__slug=movie_slug)

    if session_date:
        queryset = queryset.filter(session_date=session_date)

    return queryset


def set_ukrainian_locale():
    """Set local on Ukrainian or fallback on `C`."""
    try:
        locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_TIME, 'C')


def get_movie_by_slug(movie_slug):
    """Retrieve movie on `slug`, if exists."""
    return Movie.objects.filter(slug=movie_slug).first()


def create_stripe_session(success_url, cancel_url, order):
    if stripe is None or not settings.STRIPE_SECRET_KEY:
        return None

    session_data = {
        'mode': 'payment',
        'client_reference_id': order.id,
        'success_url': success_url,
        'cancel_url': cancel_url,
        'line_items': [],
    }

    for ticket in Ticket.objects.filter(order_id=order.id):
        session_data['line_items'].append(
            {
                'price_data': {
                    'currency': 'UAH',
                    'product_data': {
                        'name': f'Ticket for "{ticket.session.movie.title}"',
                        'description': (
                            f'Session: {ticket.session.start_time} {ticket.session.session_date}, '
                            f'Seat: {ticket.seat_number}'
                        ),
                    },
                    'unit_amount': int(ticket.session.base_ticket_price * 100),
                },
                'quantity': 1,
            }
        )
    session = stripe.checkout.Session.create(**session_data)
    return session.url


def complete_order(order):
    order.status = Order.COMPLETED
    order.save(update_fields=['status', 'updated_at'])
    order.tickets.update(status=Ticket.BOOKED)


def process_payment(request, order):
    try:
        if stripe is None or not settings.STRIPE_SECRET_KEY:
            logger.info('Stripe is not configured. Completing order in local demo mode.')
            complete_order(order)
            return request.build_absolute_uri(
                reverse('success_purchase_url', kwargs={'order_id': order.id})
            )

        success_url = request.build_absolute_uri(
            reverse('purchase_pending', kwargs={'order_id': order.id})
        )
        cancel_url = request.build_absolute_uri(
            reverse('cancel_purchase_url', kwargs={'order_id': order.id})
        )

        return create_stripe_session(success_url, cancel_url, order)
    except Exception as e:
        logger.error(f"Stripe error: {str(e)}")
        return None


def create_order_process(request, session, selected_seats, free_seats):
    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            session=session,
            status=Order.PENDING,
        )
        total_price = 0

        for seat in selected_seats:
            seat = int(seat)
            if seat not in free_seats:
                raise Exception(f'Seat {seat} is already occupied')

            Ticket.objects.create(
                session=session,
                user=request.user,
                seat_number=seat,
                status=Ticket.RESERVED,
                price=session.base_ticket_price,
                order=order,
            )
            total_price += session.base_ticket_price

        order.total_price = total_price
        order.save(update_fields=['total_price', 'updated_at'])

        redirect_url = process_payment(request, order)
        if not redirect_url:
            return False, {'error_message': 'Payment could not be completed. Please try again.'}

        return True, {'redirect_url': redirect_url}


def purchase_ticket_process(request, session):
    selected_seats = request.POST.get('selected_seats')
    if not selected_seats:
        return False, {'error_message': 'No seats selected.'}

    try:
        selected_seats = json.loads(selected_seats)
        free_seats = session.get_available_seats()

        return create_order_process(request, session, selected_seats, free_seats)
    except ValueError:
        return False, {'error_message': 'Invalid seat number.'}
    except Exception as e:
        return False, {'error_message': f'An error occurred: {str(e)}'}
