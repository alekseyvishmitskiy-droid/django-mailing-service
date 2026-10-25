from django.core.management.base import BaseCommand
from django.utils import timezone
from mailings.models import User, Recipient, Message, Mailing, MailingLog
import datetime


class Command(BaseCommand):
    help = 'Заполняет базу данных демонстрационными данными для тестирования сервиса'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Очистка старых данных...'))
        MailingLog.objects.all().delete()
        Mailing.objects.all().delete()
        Message.objects.all().delete()
        Recipient.objects.all().delete()
        # Удаляем обычных пользователей, не трогая суперпользователя (админа)
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.MIGRATE_LABEL('1. Создание тестовых пользователей...'))


        user_owner = User.objects.create_user(
            username='alexei',
            email='user@test.ru',
            password='testpassword123',
            first_name='Алексей',
            last_name='Тестовый',
            is_verified=True
        )


        user_manager = User.objects.create_user(
            username='ivan_manager',
            email='manager@test.ru',
            password='managerpassword123',
            first_name='Иван',
            last_name='Менеджеров',
            is_verified=True,
            is_manager=True
        )

        self.stdout.write(self.style.MIGRATE_LABEL('2. Создание клиентов (получателей)...'))
        client1 = Recipient.objects.create(
            email='client1@example.com',
            full_name='Иванов Иван Иванович',
            comment='Ключевой клиент',
            owner=user_owner
        )
        client2 = Recipient.objects.create(
            email='client2@example.com',
            full_name='Петров Петр Петрович',
            comment='Новый клиент',
            owner=user_owner
        )

        self.stdout.write(self.style.MIGRATE_LABEL('3. Создание сообщений...'))
        msg1 = Message.objects.create(
            subject='Добро пожаловать в наш сервис!',
            body='Здравствуйте!\nСпасибо, что выбрали наш продукт. Это тестовое письмо.'
        )
        msg2 = Message.objects.create(
            subject='Скидки и акции этой недели',
            body='Только до пятницы вас ждут персональные предложения в личном кабинете!'
        )

        self.stdout.write(self.style.MIGRATE_LABEL('4. Создание настроек рассылок...'))
        now = timezone.now()


        mailing_active = Mailing.objects.create(
            start_time=now - datetime.timedelta(hours=1),
            end_time=now + datetime.timedelta(days=2),
            message=msg1,
            owner=user_owner
        )
        mailing_active.recipients.add(client1, client2)
        mailing_active.update_status()


        mailing_future = Mailing.objects.create(
            start_time=now + datetime.timedelta(days=1),
            end_time=now + datetime.timedelta(days=5),
            message=msg2,
            owner=user_owner
        )
        mailing_future.recipients.add(client1)
        mailing_future.update_status()

        self.stdout.write(self.style.MIGRATE_LABEL('5. Логирование тестовых попыток...'))
        MailingLog.objects.create(
            status='Успешно',
            server_response='Письмо успешно отправлено через консольный бэкенд.',
            mailing=mailing_active
        )

        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена тестовыми данными!'))
