from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from mailing_list_management.models import EmailAttempt, Newsletter


class Command(BaseCommand):
    help = "Отправка рассылки по указанной рассылке"

    def add_arguments(self, parser):
        parser.add_argument("newsletter_id", type=int)

    def handle(self, *args, **kwargs):
        newsletter_id = kwargs["newsletter_id"]
        newsletter = Newsletter.objects.get(id=newsletter_id)

        if newsletter.start_time <= timezone.now() <= newsletter.end_time:
            recipients = newsletter.recipients.all()
            for recipient in recipients:
                try:
                    response = send_mail(
                        newsletter.message.subject,
                        newsletter.message.body,
                        "from@example.com",  # Замените на ваш email
                        [recipient.email],
                        fail_silently=False,
                    )

                    # Создать запись о попытке отправки
                    EmailAttempt.objects.create(
                        newsletter=newsletter,
                        recipient=recipient,
                        status="Успешно",
                        server_response=f"Письмо успешно отправлено: {response}",
                    )
                except Exception as e:
                    # Создать запись о неуспешной попытке отправки
                    EmailAttempt.objects.create(
                        newsletter=newsletter,
                        recipient=recipient,
                        status="Не успешно",
                        server_response=str(e),
                    )
            self.stdout.write(self.style.SUCCESS("Рассылка успешно отправлена!"))
        else:
            self.stdout.write(
                self.style.ERROR("Ошибка: Время для отправки рассылки недоступно.")
            )
