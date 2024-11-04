from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, DetailView, UpdateView, CreateView

from .forms import CustomLoginForm, CustomUserCreationForm, ProfileUpdateForm, CustomPasswordChangeForm
from .models import *


# superuser |  aluiel | 12365400
class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'registration/change_password.html'


class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Сохранение формы и создание пользователя
        response = super().form_valid(form)
        messages.success(self.request, 'Ви успішно зареєструвалися! Тепер ви можете увійти в систему.')
        return response


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'registration/login.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ви успішно прошли авторизацію.')
        return response


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class UserProfileSettingsView(LoginRequiredMixin, UpdateView):
    model = User  # Укажите модель пользователя
    form_class = ProfileUpdateForm  # Ваша форма для обновления профиля
    template_name = 'profile/settings.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Ваш профіль успішно оновлено.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Будь ласка, перевірте правильність введених даних.')
        return super().form_invalid(form)


class UserTicketListView(ListView):
    model = Ticket
    template_name = 'profile/ticket_list.html'

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)


class HomePageView(TemplateView):
    template_name = 'cinema_app/index.html'


class MovieListView(ListView):
    model = Movie
    template_name = 'cinema_app/movie_list.html'


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'cinema_app/movie_detail.html'


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
        movie = Movie.objects.get(slug=movie_slug)  # Получаем объект фильма
        context['movie'] = movie  # Добавляем фильм в контекст
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


def purchase_success(request, seat_number, price, session_id):
    session = get_object_or_404(Session, id=session_id)

    context = {
        'seat_number': seat_number,
        'price': price,
        'session': session,
    }
    return render(request, 'cinema_app/purchase_success.html', context)


def get_available_seats(request, session_slug):
    session = get_object_or_404(Session, slug=session_slug)
    available_seats = session.get_available_seats()

    return JsonResponse({'available_seats': available_seats})


@login_required
def purchase_ticket(request, session_slug):
    session = get_object_or_404(Session, slug=session_slug)

    available_seats = session.get_available_seats()
    total_seats = list(range(1, session.hall.capacity + 1))
    seats_per_row = 10
    row_capacity = session.hall.capacity // seats_per_row

    seats_by_row = []

    for row in range(row_capacity):
        row_seats = []
        for seat_number in range(1, seats_per_row + 1):
            seat_index = row * seats_per_row + seat_number
            if seat_index in available_seats:
                row_seats.append((seat_index, 'Free'))
            else:
                row_seats.append((seat_index, 'Booked'))
        seats_by_row.append(row_seats)

    if request.method == 'POST':
        selected_seat = request.POST.get('selected_seats')
        if selected_seat:
            try:
                selected_seat = int(selected_seat)
                price = session.base_ticket_price
                if not Ticket.objects.filter(session=session, user=request.user, seat_number=selected_seat).exists():
                    Ticket.objects.create(session=session, user=request.user, seat_number=selected_seat, price=price)
                    return redirect('success_purchase_url', seat_number=selected_seat, price=int(price), session_id=session.id)
                else:
                    messages.error(request, "Квиток з таким місцем вже існує")
            except ValueError:
                messages.error(request, "Неправильний номер місця")

            except Exception as e:
                messages.error(request, "Сталася помилка при створенні квитка: {}".format(str(e)))

        else:
            messages.error(request, "Не вибрано місце")

    context = {
        'session': session,
        'seats': seats_by_row,
    }

    return render(request, 'cinema_app/purchase_ticket.html', context)
