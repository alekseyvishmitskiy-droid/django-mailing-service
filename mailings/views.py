import secrets
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, TemplateView
from django.db.models import Count, Q
from django.core.cache import cache
from django.conf import settings
from django.contrib import messages
from .models import Mailing, Recipient, MailingLog
from .forms import UserRegisterForm
from .mixins import OwnerOrManagerRequiredMixin
from .services import send_mailing_manually

User = get_user_model()




class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('mailings:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.token = secrets.token_hex(16)
        user.save()

        host = self.request.get_host()
        url = f"http://{host}{reverse('mailings:verify', kwargs={'token': user.token})}"

        send_mail(
            subject="Активация аккаунта",
            message=f"Для активации учетной записи перейдите по ссылке: {url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        return super().form_valid(form)


def verify_email(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.is_verified = True
    user.token = None
    user.save()
    return render(request, 'registration/verification_success.html')




class MainPageView(TemplateView):
    template_name = 'mailings/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user


        cache_key = f'main_page_stats_{user.id if user.is_authenticated else "anonymous"}'


        stats_data = cache.get(cache_key)

        if not stats_data:
            if user.is_authenticated and not getattr(user, 'is_manager', False):
                mailings_qs = Mailing.objects.filter(owner=user)
                recipients_qs = Recipient.objects.filter(owner=user)
                logs_qs = MailingLog.objects.filter(mailing__owner=user)
            else:
                mailings_qs = Mailing.objects.all()
                recipients_qs = Recipient.objects.all()
                logs_qs = MailingLog.objects.all()

            total_mailings = mailings_qs.count()
            unique_recipients = recipients_qs.count()

            stats = logs_qs.aggregate(
                success_count=Count('id', filter=Q(status='Успешно')),
                failed_count=Count('id', filter=Q(status='Не успешно'))
            )
            success_attempts = stats['success_count'] or 0
            failed_attempts = stats['failed_count'] or 0


            stats_data = {
                'total_mailings': total_mailings,
                'unique_recipients': unique_recipients,
                'success_attempts': success_attempts,
                'failed_attempts': failed_attempts,
            }
            cache.set(cache_key, stats_data, 600)


        context.update(stats_data)
        return context


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'is_manager', False):
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=user)


class MailingDetailView(OwnerOrManagerRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class RunMailingView(LoginRequiredMixin, View):
    """Контроллер ручного запуска отправки писем"""

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        if not request.user.is_manager and mailing.owner != request.user:
            return redirect('mailings:mailing_list')

        success, message = send_mailing_manually(mailing)
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        return redirect('mailings:mailing_detail', pk=pk)
