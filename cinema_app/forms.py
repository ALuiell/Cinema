from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
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
    email = forms.EmailField(required=True, help_text="Обов'язково вкажіть дійсний email")

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', placeholder='Логін'),
            Field('password', placeholder='Пароль'),
            Submit('submit', 'Увійти'),
        )
