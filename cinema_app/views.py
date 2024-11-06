import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_control
from django.views.generic import ListView, TemplateView, DetailView

from cinema import settings
from .models import *


class HomePageView(TemplateView):
    template_name = 'cinema_app/index.html'


class MovieListView(ListView):
    model = Movie
    template_name = 'cinema_app/movie_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'cinema_app/movie_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


class MovieSessionsView(ListView):
    model = Session
    template_name = 'cinema_app/movie_sessions.html'
    context_object_name = 'movie_session_list'

    def get_queryset(self):
        movie_slug = self.kwargs['slug']
        return Session.objects.filter(movie__slug=movie_slug, session_date__gte=date.today())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie_slug = self.kwargs['slug']
        movie = Movie.objects.get(slug=movie_slug)
        context['movie'] = movie
        return context


class MovieGenreListView(ListView):
    model = Movie
    template_name = 'movie_list.html'
    context_object_name = 'movie_list'

    def get_queryset(self):
        genre_name = self.kwargs.get('genre_name').strip()
        return Movie.objects.filter(genre__name=genre_name)


class SessionListView(ListView):
    model = Session
    template_name = 'cinema_app/session_list.html'
    context_object_name = 'session_list'

    def get_queryset(self):
        return Session.objects.filter(session_date__gte=date.today()).order_by('session_date', 'start_time')


class SessionDetailView(DetailView):
    model = Session
    template_name = 'cinema_app/session_detail.html'
    context_object_name = 'session_detail'



def get_available_seats(request, session_slug):
    session = get_object_or_404(Session, slug=session_slug)
    available_seats = session.get_available_seats()

    return JsonResponse({'available_seats': available_seats})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
def purchase_ticket(request, session_slug):
    session = get_object_or_404(Session, slug=session_slug)
    available_seats = session.get_available_seats()
    seats_per_row = 10
    row_capacity = session.hall.capacity // seats_per_row

    seats_by_row = [
        [
            (row * seats_per_row + seat_number,
             'Free' if (row * seats_per_row + seat_number) in available_seats else 'Booked')
            for seat_number in range(1, seats_per_row + 1)
        ]
        for row in range(row_capacity)
    ]

    if request.method == 'POST':
        success, result = purchase_ticket_process(request, session)

        if success:
            return redirect('success_purchase_url', session_id=result['session_id'], ticket_ids=result['ticket_ids'])
        else:
            messages.error(request, result)

    context = {
        'session': session,
        'seats': seats_by_row,
    }

    return render(request, 'cinema_app/purchase_ticket.html', context)


def purchase_ticket_process(request, session):
    selected_seats = request.POST.get('selected_seats')
    if not selected_seats:
        return False, "Не вибрано місце"

    try:
        selected_seats = json.loads(selected_seats)
        price = session.base_ticket_price
        tickets = []

        existing_tickets = Ticket.objects.filter(session=session, user=request.user).values_list('seat_number', flat=True)

        for seat in selected_seats:
            seat = int(seat)
            if seat in existing_tickets:
                return False, f"Місця зайняті"

            ticket = Ticket.objects.create(session=session, user=request.user, seat_number=seat, price=price)
            tickets.append(ticket)

        ticket_ids = [ticket.id for ticket in tickets]
        request.POST = request.POST.copy()
        return True, {'session_id': session.id, 'ticket_ids': json.dumps(ticket_ids)}

    except ValueError:
        return False, "Неправильний номер місця"
    except Exception as e:
        return False, f"Сталася помилка при створенні квитка: {str(e)}"


def purchase_success(request, session_id, ticket_ids):
    session = get_object_or_404(Session, id=session_id)

    ticket_ids = json.loads(ticket_ids)
    tickets = Ticket.objects.filter(id__in=ticket_ids)
    seat_numbers = [ticket.seat_number for ticket in tickets]

    context = {
        'seat_numbers': seat_numbers,
        'price': session.base_ticket_price * len(seat_numbers),
        'session': session,
    }

    return render(request, 'cinema_app/purchase_success.html', context)
