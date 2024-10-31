from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Старий пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введіть старий пароль'})  # Добавление атрибутов
    )
    new_password1 = forms.CharField(
        label='Новий пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введіть новий пароль'})
    )
    new_password2 = forms.CharField(
        label='Підтвердження пароля',
        widget=forms.PasswordInput(attrs={'placeholder': 'Підтвердіть новий пароль'})
    )


class CustomUserCreationForm(UserCreationForm):

    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
        help_text="Ваш пароль має бути не менше 8 символів."
    )

    password2 = forms.CharField(
        label="Підтвердження пароля",
        widget=forms.PasswordInput,
        help_text="Введіть пароль ще раз, для підтвердження."
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Логін',
        }
        help_texts = {
            'username': 'Ваш унікальний логін.',
            'email': 'Обов’язково вкажіть дійсний email.',
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Логін"
        self.fields['password'].label = "Пароль"
