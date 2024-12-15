import locale

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.dateparse import parse_date
from django.views.decorators.cache import cache_control
from django.views.generic import ListView, TemplateView, DetailView

from cinema import settings
from .models import *
from django.db.models import Q
from .services import purchase_ticket_process, process_payment


def redirect_to_home(request):
    return redirect("home")


class HomePageView(TemplateView):
    template_name = 'cinema_app/index.html'


class MovieListView(ListView):
    model = Movie
    template_name = 'cinema_app/movie_list.html'
    context_object_name = 'movie_list'
    paginate_by = 3

    def get_queryset(self):
        queryset = super().get_queryset()
        selected_genres = self.request.GET.getlist('genre')
        age_limit = self.request.GET.get('age_limit')
        search_query = self.request.GET.get('search', '')

        if selected_genres and "" not in selected_genres:
            queryset = queryset.filter(genre__id__in=selected_genres).distinct()
        if age_limit:
            queryset = queryset.filter(age_limit=age_limit)
        if search_query:
            search_query = search_query.capitalize()
            query = Q(title__icontains=search_query) | Q(description__icontains=search_query) | Q(
                original_name__icontains=search_query)
            queryset = queryset.filter(query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Genre.objects.all()
        context['selected_genres'] = self.request.GET.getlist('genre')
        context['selected_age_limit'] = self.request.GET.get('age_limit')
        context['search_query'] = self.request.GET.get('search', '')
        context['AGE_CHOICES'] = Movie.AGE_CHOICES
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'cinema_app/movie_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


class SessionListView(ListView):
    model = Session
    template_name = 'cinema_app/session_list.html'
    context_object_name = 'session_list'

    def get_queryset(self):
        sessions = Session.objects.filter(session_date__gte=date.today()).order_by('session_date', 'start_time')

        # Проверяем наличие slug фильма в параметрах URL
        movie_slug = self.kwargs.get('slug')
        if movie_slug:
            # Фильтруем сессии только по slug фильма
            sessions = sessions.filter(movie__slug=movie_slug)

        selected_date = self.request.GET.get('date', None)
        if selected_date:
            selected_date = parse_date(selected_date)
            if selected_date:
                sessions = sessions.filter(session_date=selected_date)

        return sessions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Устанавливаем локаль на украинский
        locale.setlocale(locale.LC_TIME, 'uk_UA.UTF-8')

        today = date.today()
        selected_date = self.request.GET.get('date', None)

        # Если selected_date не передан, то используем today's date как default
        if selected_date:
            selected_date = parse_date(selected_date)

        # Добавляем информацию о фильме в контекст, если передан `slug`
        movie_slug = self.kwargs.get('slug')
        if movie_slug:
            movie = Movie.objects.get(slug=movie_slug)
            context['movie'] = movie

        context.update({
            'today': today,
            'today_label': "Сьогодні",
            'tomorrow': today + timedelta(days=1),
            'tomorrow_label': "Завтра",
            'upcoming_days': [
                {'date': today + timedelta(days=i), 'label': (today + timedelta(days=i)).strftime('%A %d.%m')}
                for i in range(2, 5)
            ],
            'selected_date': selected_date,
        })

        return context


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
    # List comprehension to create seat data with unique IDs and their availability status
    seats_by_row = [
        [
            (row * seats_per_row + seat_number,
             'Free' if (row * seats_per_row + seat_number) in available_seats else 'Booked')
            for seat_number in range(1, seats_per_row + 1)
        ]
        for row in range(row_capacity)
    ]

    if request.method == 'POST':
        # success, result, order_id = purchase_ticket_process(request, session)
        success, data = purchase_ticket_process(request, session)
        if not success:
            messages.error(request, data["error_message"])
        else:
            return redirect(data['redirect_url'])

    context = {
        'session': session,
        'seats': seats_by_row,
    }

    return render(request, 'payments/purchase_ticket.html', context)


@login_required
def retry_payment(request, pk):
    order = get_object_or_404(Order, id=pk)
    redirect_url = process_payment(request, order)
    if redirect_url:
        return redirect(redirect_url)
    else:
        messages.error(request, 'Щось пішло не так')
        return redirect('home')


def check_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if order.user != request.user:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    return JsonResponse({'status': order.status})


def purchase_pending(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'payments/purchase_pending.html', context)


def purchase_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user != request.user:
        messages.error(request, "You are not allowed to view this order.")
        return redirect('home')

    seat_numbers = order.get_seat_numbers()

    context = {
        'seat_numbers': seat_numbers,
        'price': order.total_price,
        'session': order.session,
    }

    return render(request, 'payments/purchase_success.html', context)


def purchase_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user != request.user:
        messages.error(request, "You are not allowed to view this order.")
        return redirect('home')

    seat_numbers = order.get_seat_numbers()

    context = {
        'seat_numbers': seat_numbers,
        'price': order.total_price,
        'session': order.session,
        'order': order,
    }

    return render(request, 'payments/purchase_cancel.html', context)
