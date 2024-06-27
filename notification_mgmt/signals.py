from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import NotificationPreference, NotificationType


@receiver(post_save, sender=User)
def create_default_notification_preferences(sender, instance, created, **kwargs):
    if created:
        notification_types = NotificationType.objects.all()
        for notif_type in notification_types:
            NotificationPreference.objects.create(user=instance, notification_type=notif_type)


@receiver(post_save, sender=NotificationType)
def update_notification_type_for_all_users(sender, instance, created, **kwargs):
    if created:
        users = User.objects.all()
        for user in users:
            NotificationPreference.objects.create(user=user, notification_type=instance)
