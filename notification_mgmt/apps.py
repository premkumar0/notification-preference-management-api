from django.apps import AppConfig


class NotificationMgmtConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "notification_mgmt"

    def ready(self):
        import notification_mgmt.signals
