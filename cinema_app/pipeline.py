from django.contrib import messages
from django.shortcuts import redirect


def check_email_exists(strategy, details, user=None, backend=None, request=None, *args, **kwargs):
    """
    Перевіряє, чи існує користувач із таким email.
    Якщо так, то виводить повідомлення про помилку і перенаправляє на сторінку входу.
    """
    from django.contrib.auth.models import User

    email = details.get('email')
    if email and not user:
        try:
            User.objects.get(email=email)
            messages.error(request, "Аккаунт з таким email вже існує. Увійдіть в існуючий аккаунт")
            return redirect('login')

        except User.DoesNotExist:
            pass
