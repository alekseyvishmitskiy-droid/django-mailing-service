from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    """Форма для регистрации нового пользователя"""
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email", "username")


class UserLoginForm(AuthenticationForm):
    """🟢 ДОБАВЛЕНО: Кастомная форма для входа в систему через Email"""
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com',
            'id': 'username'
        }),
        label="Email"
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••'
        }),
        label="Пароль"
    )
