from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from mailing_list_management.forms import (MessageForm, NewsletterForm,
                                           RecipientForm)
from mailing_list_management.models import (EmailAttempt, Message, Newsletter,
                                            Recipient)


def homepage(request):
    # Общее количество всех созданных рассылок
    total_newsletters = Newsletter.objects.count()

    # Количество активных рассылок
    current_time = timezone.now()
    active_newsletters = Newsletter.objects.filter(
        start_time__lte=current_time, end_time__gte=current_time, status="Запущена"
    ).count()

    # Количество уникальных получателей
    unique_recipients = Recipient.objects.count()

    # Количество успешных и неуспешных попыток рассылок
    successful_attempts = EmailAttempt.objects.filter(status="Успешно").count()
    failed_attempts = EmailAttempt.objects.filter(status="Не успешно").count()

    # Количество отправленных сообщений
    sent_messages = successful_attempts + failed_attempts

    context = {
        "total_newsletters": total_newsletters,
        "active_newsletters": active_newsletters,
        "unique_recipients": unique_recipients,
        "successful_attempts": successful_attempts,
        "failed_attempts": failed_attempts,
        "sent_messages": sent_messages,
    }
    return render(request, "../templates/MailingListManagement/homepage.html", context)


# Работы с получателями
class RecipientListView(ListView):
    model = Recipient
    template_name = "../templates/MailingListManagement/recipient_list.html"  # Замените на ваш шаблон
    context_object_name = "recipients"

    def get_queryset(self):
        return Recipient.objects.filter(owner=self.request.user)


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "../templates/MailingListManagement/recipient_form.html"  # Замените на ваш шаблон
    success_url = reverse_lazy("mailing_list_management:recipient_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientDetailView(DetailView):
    model = Recipient
    template_name = "../templates/MailingListManagement/recipient_detail.html"


class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "../templates/MailingListManagement/recipient_form.html"  # Замените на ваш шаблон
    success_url = reverse_lazy("mailing_list_management:recipient_list")


class RecipientDeleteView(DeleteView):
    model = Recipient
    template_name = "../templates/MailingListManagement/recipient_confirm_delete.html"  # Замените на ваш шаблон
    success_url = reverse_lazy("mailing_list_management:recipient_list")


# Работы с сообщениями
class MessageListView(ListView):
    model = Message
    template_name = (
        "../templates/MailingListManagement/message_list.html"  # Замените на ваш шаблон
    )
    context_object_name = "messages"

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = (
        "../templates/MailingListManagement/message_form.html"  # Замените на ваш шаблон
    )
    success_url = reverse_lazy("mailing_list_management:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageDetailView(DetailView):
    model = Message
    template_name = "../templates/MailingListManagement/message_detail.html"


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = (
        "../templates/MailingListManagement/message_form.html"  # Замените на ваш шаблон
    )
    success_url = reverse_lazy("mailing_list_management:message_list")


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "../templates/MailingListManagement/message_confirm_delete.html"  # Замените на ваш шаблон
    success_url = reverse_lazy("mailing_list_management:message_list")


# Работы с рассылками
class NewsletterListView(ListView):
    model = Newsletter
    template_name = "../templates/MailingListManagement/newsletter_list.html"  # Замените на ваш шаблон
    context_object_name = "newsletters"

    def get_queryset(self):
        return Newsletter.objects.filter(owner=self.request.user)


class NewsletterCreateView(CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = "../templates/MailingListManagement/newsletter_form.html"  # Замените на ваш шаблон
    success_url = reverse_lazy("mailing_list_management:newsletter_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class NewsletterDetailView(DetailView):
    model = Newsletter
    template_name = "../templates/MailingListManagement/newsletter_detail.html"


class NewsletterUpdateView(UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = "../templates/MailingListManagement/newsletter_form.html"  # Замените на ваш шаблон
    success_url = reverse_lazy("mailing_list_management:newsletter_list")


class NewsletterDeleteView(DeleteView):
    model = Newsletter
    template_name = "../templates/MailingListManagement/newsletter_confirm_delete.html"  # Замените на ваш шаблон
    success_url = reverse_lazy("mailing_list_management:newsletter_list")


class NewsletterDetailView(DetailView):
    model = Newsletter
    template_name = "../templates/MailingListManagement/newsletter_detail.html"  # Замените на ваш шаблон

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # Обновляем статус при просмотре
        return obj


class SendNewsletterView(View):
    template_name = "../templates/MailingListManagement/newsletter_send.html"  # Замените на ваш шаблон

    def get(self, request, pk):
        newsletter = get_object_or_404(Newsletter, pk=pk)
        return render(request, self.template_name, {"newsletter": newsletter})

    def post(self, request, pk):
        newsletter = get_object_or_404(Newsletter, pk=pk)

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
            messages.success(request, "Рассылка успешно отправлена!")
            return redirect("newsletter_list")
        else:
            messages.error(request, "Ошибка: Время для отправки рассылки недоступно.")
            return render(request, self.template_name, {"newsletter": newsletter})
