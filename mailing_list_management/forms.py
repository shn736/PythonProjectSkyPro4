from django import forms

from mailing_list_management.models import Message, Newsletter, Recipient


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ["email", "full_name", "comment"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["subject", "body"]


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ["start_time", "end_time", "message", "recipients"]
