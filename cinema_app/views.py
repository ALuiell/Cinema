from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.dateparse import parse_date
from django.views.decorators.cache import cache_control
from django.views.generic import ListView, TemplateView, DetailView
from cinema import settings
from .models import *
from cinema_app import services


def redirect_to_home(request):
    return redirect("home")


class HomePageView(TemplateView):
    template_name = 'cinema_app/index.html'


class MovieListView(ListView):
    model = Movie
    template_name = 'cinema_app/movie_list.html'
    context_object_name = 'movie_list'
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()

        # Retrieve query parameters from the request
        selected_genres = self.request.GET.getlist('genre')
        age_limit = self.request.GET.get('age_limit')
        search_query = self.request.GET.get('search', '').strip()

        queryset = services.get_movies_list(queryset, selected_genres, age_limit, search_query)

        return queryset.order_by('id')

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
        queryset = Session.objects.filter(
            session_date__gte=date.today()
        ).order_by('session_date', 'start_time')

        movie_slug = self.kwargs.get('slug')

        date_str = self.request.GET.get('date')
        if date_str:
            selected_date = parse_date(date_str)
            if not selected_date:
                selected_date = date.today()
        else:
            selected_date = date.today()

        return services.get_sessions_list(
            queryset,
            movie_slug,
            selected_date
        )


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services.set_ukrainian_locale()

        today = date.today()
        selected_date = self.request.GET.get('date', None)

        # If selected_date is not passed, then we use today's date as default
        if selected_date:
            selected_date = parse_date(selected_date)

        # Add movie information to the context if `slug` is passed in
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
    seats_by_row = session.get_seats_by_row()

    if request.method == 'POST':
        success, data = services.purchase_ticket_process(request, session)
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
    redirect_url = services.process_payment(request, order)
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
    seat_numbers = order.get_str_seat_numbers()
    context = {
        'order': order,
        'seat_numbers': seat_numbers,
    }
    return render(request, 'payments/purchase_pending.html', context)


def purchase_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.user != request.user:
        messages.error(request, "You are not allowed to view this order.")
        return redirect('home')

    seat_numbers = order.get_str_seat_numbers()

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

    seat_numbers = order.get_str_seat_numbers()

    context = {
        'seat_numbers': seat_numbers,
        'price': order.total_price,
        'session': order.session,
        'order': order,
    }

    return render(request, 'payments/purchase_cancel.html', context)

@login_required
def start_telegram_link(request):
    url = TelegramProfile.create_instance(request.user)
    return redirect(url["deep_link"])