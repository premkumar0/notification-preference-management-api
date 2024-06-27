from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from notification_mgmt.models import NotificationPreference, NotificationType
from notification_mgmt.serializers import (
    NotificationPreferenceSerializer,
    NotificationTypeSerializer,
)


class NotificationTypeViewSet(viewsets.ModelViewSet):
    queryset = NotificationType.objects.all()
    serializer_class = NotificationTypeSerializer

    def get_permissions(self):
        if self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.permission_classes = [IsAdminUser]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()


class NotificationPreferenceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put"]

    def get_queryset(self):
        user = self.request.user
        return NotificationPreference.objects.filter(user=user)

    def list(self, request):
        """
        Retrieve all notification types and their preferences for the authenticated user.
        """
        preferences = self.get_queryset()
        serializer = NotificationPreferenceSerializer(preferences, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["put"], permission_classes=[IsAuthenticated])
    def update_preferences(self, request):
        """
        Update the notification preferences for the authenticated user.
        """
        preferences_data = request.data
        queryset = self.get_queryset()

        for preference_data in preferences_data:
            notification_type = preference_data.get("notification_type")
            if notification_type:
                notification_type_name = notification_type.get("name")
            else:
                return Response(
                    "Invalid Notification type passed", status=status.HTTP_400_BAD_REQUEST
                )

            instance = queryset.filter(
                notification_type__name=notification_type_name, user=request.user
            ).first()

            if instance:
                preference_data.pop("notification_type")
                serializer = NotificationPreferenceSerializer(
                    instance, data=preference_data, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {
                        "detail": f"Notification type '{notification_type_name}' not found for user {request.user.username}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )
        return Response({"status": "preferences updated successfullyu"}, status=status.HTTP_200_OK)
