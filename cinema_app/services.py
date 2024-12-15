import json

import stripe
from django.conf import settings
from django.db import transaction

from .models import *

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


def process_payment(request, order):
    try:
        """
        Emulation payment process
        return True if payment succeeded, False if payment failed.
        """
        success_url = request.build_absolute_uri(reverse('success_purchase_url', kwargs={
            'order_id': order.id
        }))
        cancel_url = request.build_absolute_uri(reverse('cancel_purchase_url', kwargs={
            'order_id': order.id
        }))

        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': [],
        }

        for ticket in Ticket.objects.filter(order_id=order.id):
            session_data['line_items'].append({
                'price_data': {
                    'currency': 'UAH',
                    'product_data': {
                        'name': f'Квиток на "{ticket.session.movie.title}"',
                        'description': f'Сеанс: {ticket.session.start_time} {ticket.session.session_date}, '
                                       f'Місце: {ticket.seat_number}',
                    },
                    'unit_amount': int(ticket.session.base_ticket_price * 100),
                },
                'quantity': 1,
            })

        session = stripe.checkout.Session.create(**session_data)

        # return redirect_url in purchase_ticket_process
        return session.url

    except stripe.error.StripeError as e:
        print(f"Stripe error: {str(e)}")
        return None


def purchase_ticket_process(request, session):
    selected_seats = request.POST.get('selected_seats')
    if not selected_seats:
        return False, "Не вибрано місце"

    try:
        selected_seats = json.loads(selected_seats)
        price = session.base_ticket_price
        total_price = price * len(selected_seats)

        with transaction.atomic():
            order = Order.objects.create(user=request.user, session=session, total_price=total_price,
                                         status=Order.PENDING)
            tickets = []

            existing_tickets = set(
                Ticket.objects.filter(session=session).values_list('seat_number', flat=True)
            )

            for seat in selected_seats:
                seat = int(seat)
                if seat in existing_tickets:
                    return False, f"Місце {seat} вже зайняте"

                ticket = Ticket.objects.create(
                    session=session, user=request.user, seat_number=seat, status=Ticket.RESERVED, price=price,
                    order=order
                )
                tickets.append(ticket)

            redirect_url = process_payment(request, order)

            if not redirect_url:
                return False, "Оплата не прошла. Спробуйте ще раз", order.id

            # return redirect_url in main function purchase_ticket
            return redirect_url, order.id

    except ValueError:
        return False, "Неправильний номер місця"
    except Exception as e:
        return False, f"Сталася помилка: {str(e)}"
