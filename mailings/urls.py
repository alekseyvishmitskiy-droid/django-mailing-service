from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.views.decorators.cache import cache_page
from .apps import MailingsConfig
from .views import MainPageView, MailingListView, MailingDetailView, RegisterView, verify_email, RunMailingView

app_name = MailingsConfig.name

urlpatterns = [
    path('', MainPageView.as_view(), name='index'),
    path('mailings/', cache_page(60)(MailingListView.as_view()), name='mailing_list'),
    path('mailings/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/<int:pk>/run/', RunMailingView.as_view(), name='run_mailing'),

    # Профили пользователей и регистрация
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify/<str:token>/', verify_email, name='verify'),

    # Восстановление пароля
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        success_url=reverse_lazy('mailings:password_reset_done')
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('mailings:password_reset_complete')
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]
