from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import Mailing, MailingLog


def send_mailing_manually(mailing: Mailing) -> tuple[bool, str]:
    """Выполняет ручной или автоматический запуск отправки писем"""
    now = timezone.now()
    mailing.update_status()


    if not (mailing.start_time <= now <= mailing.end_time):
        return False, f"Ошибка: Время {now.strftime('%d.%m.%Y %H:%M')} вне интервала работы рассылки."


    recipients = mailing.recipients.all()
    if not recipients:
        return False, "Ошибка: У рассылки нет получателей."

    recipient_emails = [client.email for client in recipients]


    try:
        send_mail(
            subject=mailing.message.subject,
            message=mailing.message.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_emails,
            fail_silently=False,
        )

        MailingLog.objects.create(
            status='Успешно',
            server_response="Сообщение успешно доставлено всем получателям.",
            mailing=mailing
        )
        return True, "Рассылка успешно выполнена."

    except Exception as e:
        MailingLog.objects.create(
            status='Не успешно',
            server_response=str(e),
            mailing=mailing
        )
        return False, f"Ошибка при отправке: {e}"
