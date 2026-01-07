from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Recipient(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.full_name


class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()

    def __str__(self):
        return self.subject


class Newsletter(models.Model):
    STATUS_CHOICES = [
        ("Создана", "Создана"),
        ("Запущена", "Запущена"),
        ("Завершена", "Завершена"),
    ]

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Создана")
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    recipients = models.ManyToManyField(Recipient)

    def clean(self):
        # Валидация полей
        if self.start_time < timezone.now():
            raise ValidationError("Дата начала не может быть в прошлом.")
        if self.start_time >= self.end_time:
            raise ValidationError("Дата начала должна быть раньше даты окончания.")

    def update_status(self):
        current_time = timezone.now()
        new_status = self.status

        if current_time < self.start_time:
            new_status = "Создана"
        elif self.start_time <= current_time <= self.end_time:
            new_status = "Запущена"
        else:
            new_status = "Завершена"

        if new_status != self.status:
            self.status = new_status
            self.save()

    def save(self, *args, **kwargs):
        # Вызываем валидацию
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Рассылка: {self.message.subject}"


class EmailAttempt(models.Model):
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    attempt_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    server_response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.newsletter} - {self.recipient.email}: {self.status}"
