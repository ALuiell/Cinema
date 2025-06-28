from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, UpdateView
from .forms import ProfileUpdateForm
from .models import *


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class UserProfileSettingsView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileUpdateForm
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


class UserOrderListView(ListView):
    model = Order
    template_name = 'profile/order_list.html'
    paginate_by = 3

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
