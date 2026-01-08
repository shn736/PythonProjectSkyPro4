from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from config.settings import CACHE_ENABLED
from mailing_list_management.forms import MessageForm, NewsletterForm, RecipientForm
from mailing_list_management.models import EmailAttempt, Message, Newsletter, Recipient
from mailing_list_management.services import (get_messages_from_cache, get_newsletters_from_cache,
                                              get_recipients_from_cache)


def homepage(request):
    total_newsletters = Newsletter.objects.count()

    current_time = timezone.now()
    active_newsletters = Newsletter.objects.filter(
        start_time__lte=current_time, end_time__gte=current_time, status="Запущена"
    ).count()

    unique_recipients = Recipient.objects.count()

    successful_attempts = EmailAttempt.objects.filter(status="Успешно").count()
    failed_attempts = EmailAttempt.objects.filter(status="Не успешно").count()

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


class RecipientListView(ListView):
    model = Recipient
    template_name = "../templates/MailingListManagement/recipient_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        if not CACHE_ENABLED:
            return Recipient.objects.filter(owner=self.request.user)
        recipients = get_recipients_from_cache(self.request.user)
        if recipients is None:
            recipients = Recipient.objects.filter(owner=self.request.user)
            cache.set(self.request.user, recipients)

        return recipients


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "../templates/MailingListManagement/recipient_form.html"
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
    template_name = "../templates/MailingListManagement/recipient_form.html"
    success_url = reverse_lazy("mailing_list_management:recipient_list")


class RecipientDeleteView(DeleteView):
    model = Recipient
    template_name = "../templates/MailingListManagement/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailing_list_management:recipient_list")


class MessageListView(ListView):
    model = Message
    template_name = "../templates/MailingListManagement/message_list.html"
    context_object_name = "messages"

    def get_queryset(self):
        if not CACHE_ENABLED:
            return Message.objects.filter(owner=self.request.user)
        messages = get_messages_from_cache(self.request.user)
        if messages is None:
            messages = Message.objects.filter(owner=self.request.user)
            cache.set(self.request.user, messages)

        return messages


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = "../templates/MailingListManagement/message_form.html"
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
    template_name = "../templates/MailingListManagement/message_form.html"
    success_url = reverse_lazy("mailing_list_management:message_list")


class MessageDeleteView(DeleteView):
    model = Message
    template_name = "../templates/MailingListManagement/message_confirm_delete.html"
    success_url = reverse_lazy("mailing_list_management:message_list")


# Работы с рассылками
class NewsletterListView(ListView):
    model = Newsletter
    template_name = "../templates/MailingListManagement/newsletter_list.html"
    context_object_name = "newsletters"

    def get_queryset(self):
        if not CACHE_ENABLED:
            return Newsletter.objects.filter(owner=self.request.user)
        newsletters = get_newsletters_from_cache(self.request.user)
        if newsletters is None:
            newsletters = Newsletter.objects.filter(owner=self.request.user)
            cache.set(self.request.user, newsletters)

        return newsletters


class NewsletterCreateView(CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = "../templates/MailingListManagement/newsletter_form.html"
    success_url = reverse_lazy("mailing_list_management:newsletter_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class NewsletterUpdateView(UpdateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = "../templates/MailingListManagement/newsletter_form.html"
    success_url = reverse_lazy("mailing_list_management:newsletter_list")


class NewsletterDeleteView(DeleteView):
    model = Newsletter
    template_name = "../templates/MailingListManagement/newsletter_confirm_delete.html"
    success_url = reverse_lazy("mailing_list_management:newsletter_list")


class NewsletterDetailView(DetailView):
    model = Newsletter
    template_name = "../templates/MailingListManagement/newsletter_detail.html"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # Обновляем статус при просмотре
        return obj


class SendNewsletterView(View):
    template_name = "../templates/MailingListManagement/newsletter_send.html"

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
                        "from@example.com",
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
