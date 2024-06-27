from django.core.management.base import BaseCommand
from notification_mgmt.models import NotificationType


class Command(BaseCommand):
    help = "Create default notification types"

    def handle(self, *args, **kwargs):
        notification_types = NotificationType.NOTIFICATOON_TYPES

        for nt_type, nt_desc in notification_types:
            notification_type, created = NotificationType.objects.get_or_create(name=nt_type)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created notification type: {nt_desc}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"Notification type already exists: {nt_desc}")
                )
