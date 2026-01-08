from django.urls import path
from django.views.decorators.cache import cache_page

from mailing_list_management.apps import MailingListManagementConfig

from .views import (
    MessageCreateView,
    MessageDeleteView,
    MessageDetailView,
    MessageListView,
    MessageUpdateView,
    NewsletterCreateView,
    NewsletterDeleteView,
    NewsletterDetailView,
    NewsletterListView,
    NewsletterUpdateView,
    RecipientCreateView,
    RecipientDeleteView,
    RecipientDetailView,
    RecipientListView,
    RecipientUpdateView,
    SendNewsletterView,
    homepage,
)

app_name = MailingListManagementConfig.name

urlpatterns = [
    # Получатели
    path("", homepage, name="homepage"),
    path("recipients/", RecipientListView.as_view(), name="recipient_list"),
    path("recipients/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path(
        "recipients/<int:pk>/",
        cache_page(60)(RecipientDetailView.as_view()),
        name="recipient",
    ),
    path(
        "recipients/update/<int:pk>/",
        RecipientUpdateView.as_view(),
        name="recipient_update",
    ),
    path(
        "recipients/delete/<int:pk>/",
        RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
    # Сообщения
    path("messages/", MessageListView.as_view(), name="message_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path(
        "messages/<int:pk>/",
        cache_page(60)(MessageDetailView.as_view()),
        name="message",
    ),
    path("messages/update/<int:pk>/", MessageUpdateView.as_view(), name="message_update"),
    path("messages/delete/<int:pk>/", MessageDeleteView.as_view(), name="message_delete"),
    # Рассылки
    path("newsletters/", NewsletterListView.as_view(), name="newsletter_list"),
    path("newsletters/create/", NewsletterCreateView.as_view(), name="newsletter_create"),
    path(
        "newsletters/<int:pk>/",
        cache_page(60)(NewsletterDetailView.as_view()),
        name="newsletter",
    ),
    path(
        "newsletters/update/<int:pk>/",
        NewsletterUpdateView.as_view(),
        name="newsletter_update",
    ),
    path(
        "newsletters/delete/<int:pk>/",
        NewsletterDeleteView.as_view(),
        name="newsletter_delete",
    ),
    path(
        "newsletters/<int:pk>/",
        NewsletterDetailView.as_view(),
        name="newsletter_detail",
    ),
    path(
        "newsletters/send/<int:pk>/",
        SendNewsletterView.as_view(),
        name="newsletter_send",
    ),
]
