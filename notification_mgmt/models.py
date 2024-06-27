from django.contrib.auth.models import User
from django.db import models


class NotificationType(models.Model):
    NOTIFICATOON_TYPES = [
        ("TOP_PRIORITIES", "Top Priorities"),
        ("SCORE_CHANGES", "Score Changes"),
        ("BUDGETING_AND_SPENDING", "Budgeting & Spending"),
        ("PROFILE_UPDATES", "Profile Updates"),
        ("REPORTS_AND_RECAPS", "Reports & Recaps"),
    ]
    name = models.CharField(
        max_length=25,
        unique=True,
        choices=NOTIFICATOON_TYPES,
        error_messages={"unique": "Notification Type already exists"},
    )

    def __str__(self):
        return self.name


class NotificationPreference(models.Model):
    FREQUENCY_CHOICES = [
        ("INSTANTLY", "Instantly"),
        ("PERIODICALLY", "Periodically"),
        ("RARELY", "Rarely"),
    ]
    notification_type = models.ForeignKey(
        NotificationType, on_delete=models.CASCADE, editable=False
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, editable=False)
    frequency = models.CharField(
        max_length=13, choices=FREQUENCY_CHOICES, default=FREQUENCY_CHOICES[0][0]
    )
    email = models.BooleanField(default=False)
    push = models.BooleanField(default=False)
    sms = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.notification_type}"
