from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView, LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomLoginForm, CustomUserCreationForm, CustomPasswordChangeForm


# superuser |  aluiel | jopa12365400
# superuser |  admin | admin
class CustomPasswordChangeView(PasswordChangeView):
    form_class = CustomPasswordChangeForm
    success_url = reverse_lazy('password_change_done')
    template_name = 'registration/change_password.html'


class UserRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
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
