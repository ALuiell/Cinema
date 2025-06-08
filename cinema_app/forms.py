from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth import get_user_model


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Старий пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введіть старий пароль'})
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
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Логін',
        }
        help_texts = {
            'username': 'Ваш унікальний логін.',
            'email': 'Обов’язково вкажіть дійсний email.',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        UserModel = get_user_model()
        if UserModel.objects.filter(email=email).exists():
            raise forms.ValidationError("Ця електронна адреса вже використовується.")
        return email


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']


class CustomLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Логін"
        self.fields['password'].label = "Пароль"
