from django.contrib import messages
from django.shortcuts import redirect


def check_email_exists(strategy, details, user=None, backend=None, request=None, *args, **kwargs):
    """
    Перевіряє, чи існує користувач із таким email.
    Якщо так, то виводить повідомлення про помилку і перенаправляє на сторінку входу.
    """
    from django.contrib.auth import get_user_model
    UserModel = get_user_model()

    email = details.get('email')
    if email and user is None:
        try:
            UserModel.objects.get(email=email)
            messages.error(request, "Аккаунт з таким email вже існує. Увійдіть в існуючий аккаунт")
            return redirect('login')
        except UserModel.DoesNotExist:
            pass
