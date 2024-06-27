from rest_framework import serializers

from notification_mgmt.models import NotificationPreference, NotificationType


class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = ["id", "name"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    notification_type = NotificationTypeSerializer()

    class Meta:
        model = NotificationPreference
        fields = ["id", "notification_type", "frequency", "email", "push", "sms"]
