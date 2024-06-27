from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.utils import IntegrityError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from notification_mgmt.models import NotificationPreference, NotificationType
from notification_mgmt.signals import (
    create_default_notification_preferences,
    update_notification_type_for_all_users,
)


class NotificationTypeViewSetTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username="admin", password="admin123")
        self.normal_user = User.objects.create_user(username="user", password="user123")
        self.notification_type_data = {"name": "TOP_PRIORITIES"}

    def test_create_notification_type_as_admin(self):
        self.client.login(username="admin", password="admin123")
        response = self.client.post(
            "/api/notification-types/", self.notification_type_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_notification_type_as_non_admin(self):
        self.client.login(username="user", password="user123")
        response = self.client.post(
            "/api/notification-types/", self.notification_type_data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_notification_types_as_public(self):
        NotificationType.objects.create(name="TOP_PRIORITIES")
        response = self.client.get("/api/notification-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_notification_type_as_admin(self):
        self.client.login(username="admin", password="admin123")
        notification_type = NotificationType.objects.create(name="SCORE_CHANGES")
        response = self.client.put(
            f"/api/notification-types/{notification_type.id}/",
            {"name": "TOP_PRIORITIES"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_invalid_notification_type_as_admin(self):
        self.client.login(username="admin", password="admin123")
        notification_type = NotificationType.objects.create(name="SCORE_CHANGES")
        response = self.client.put(
            f"/api/notification-types/{notification_type.id}/",
            {"name": "INVALID_DATA"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_notification_type_as_non_admin(self):
        self.client.login(username="user", password="user123")
        notification_type = NotificationType.objects.create(name="SCORE_CHANGES")
        response = self.client.put(
            f"/api/notification-types/{notification_type.id}/",
            {"name": "TOP_PRIORITIES"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_notification_type_as_admin(self):
        self.client.login(username="admin", password="admin123")
        notification_type = NotificationType.objects.create(name="REPORTS_AND_RECAPS")
        response = self.client.delete(f"/api/notification-types/{notification_type.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class NotificationPreferenceViewSetTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="user", password="user123")
        self.notification_type_top_priorities = NotificationType.objects.create(
            name="TOP_PRIORITIES"
        )
        self.notification_type_score_changes = NotificationType.objects.create(name="SCORE_CHANGES")
        self.notification_type_bdgt_and_spends = NotificationType.objects.create(
            name="BUDGETING_AND_SPENDING"
        )
        self.notification_type_prof_updt = NotificationType.objects.create(name="PROFILE_UPDATES")
        self.notification_type_rep_and_rec = NotificationType.objects.create(
            name="REPORTS_AND_RECAPS"
        )
        self.client.login(username="user", password="user123")
        self.notification_preference = NotificationPreference.objects.filter(user=self.user).first()

    def test_list_notification_preferences(self):
        response = self.client.get("/api/notification-preferences/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)
        self.assertEqual(response.data[0]["notification_type"]["name"], "TOP_PRIORITIES")

    def test_update_notification_preferences(self):
        data = [
            {
                "notification_type": {"name": "TOP_PRIORITIES"},
                "frequency": "RARELY",
                "email": False,
                "push": True,
                "sms": True,
            }
        ]
        response = self.client.put(
            "/api/notification-preferences/update_preferences/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.notification_preference.refresh_from_db()
        self.assertEqual(self.notification_preference.frequency, "RARELY")
        self.assertEqual(self.notification_preference.email, False)
        self.assertEqual(self.notification_preference.push, True)
        self.assertEqual(self.notification_preference.sms, True)

    def test_update_notification_preferences_with_invalid_type(self):
        data = [
            {
                "notification_type": {"name": "INVALID_TYPE"},
                "frequency": "RARELY",
                "email": False,
                "push": True,
                "sms": True,
            }
        ]
        response = self.client.put(
            "/api/notification-preferences/update_preferences/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_access(self):
        self.client.logout()
        response = self.client.get("/api/notification-preferences/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        data = [
            {
                "notification_type": {"name": "TOP_PRIORITIES"},
                "frequency": "weekly",
                "email": False,
                "push": True,
                "sms": True,
            }
        ]
        response = self.client.put(
            "/api/notification-preferences/update_preferences/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class NotificationTypeTest(TestCase):

    def setUp(self):
        self.notification_type_data = {"name": "TOP_PRIORITIES"}
        NotificationType.objects.create(name="SCORE_CHANGES")

    def test_create_notification_type(self):
        notification_type = NotificationType.objects.create(**self.notification_type_data)
        self.assertEqual(notification_type.name, "TOP_PRIORITIES")

    def test_create_duplicate_notification_type(self):
        with self.assertRaises(IntegrityError):
            NotificationType.objects.create(name="SCORE_CHANGES")


class NotificationPreferenceSignalTest(TestCase):

    def setUp(self):
        post_save.disconnect(receiver=create_default_notification_preferences, sender=User)
        post_save.disconnect(
            receiver=update_notification_type_for_all_users, sender=NotificationType
        )

    def tearDown(self):
        post_save.connect(receiver=create_default_notification_preferences, sender=User)
        post_save.connect(receiver=update_notification_type_for_all_users, sender=NotificationType)

    def test_default_fields(self):
        notification_type = NotificationType.objects.create(name="TOP_PRIORITIES")
        user = User.objects.create_user(username="user", password="user123")

        notification_preference = NotificationPreference.objects.create(
            notification_type=notification_type, user=user
        )
        self.assertEqual(notification_preference.frequency, "INSTANTLY")
        self.assertFalse(notification_preference.email)
        self.assertFalse(notification_preference.push)
        self.assertFalse(notification_preference.sms)

    def test_create_default_notification_preferences_signal(self):
        notification_type1 = NotificationType.objects.create(name="TOP_PRIORITIES")
        notification_type2 = NotificationType.objects.create(name="SCORE_CHANGES")

        post_save.connect(receiver=create_default_notification_preferences, sender=User)
        user = User.objects.create_user(username="user", password="user123")
        self.assertEqual(NotificationPreference.objects.filter(user=user).count(), 2)
        self.assertTrue(
            NotificationPreference.objects.filter(
                user=user, notification_type=notification_type1
            ).exists()
        )
        self.assertTrue(
            NotificationPreference.objects.filter(
                user=user, notification_type=notification_type2
            ).exists()
        )

    def test_update_notification_type_for_all_users_signal(self):
        user1 = User.objects.create_user(username="user1", password="user123")
        user2 = User.objects.create_user(username="user2", password="user123")

        post_save.connect(receiver=update_notification_type_for_all_users, sender=NotificationType)

        notification_type = NotificationType.objects.create(name="TOP_PRIORITIES")
        self.assertEqual(
            NotificationPreference.objects.filter(notification_type=notification_type).count(), 2
        )
        self.assertTrue(
            NotificationPreference.objects.filter(
                user=user1, notification_type=notification_type
            ).exists()
        )
        self.assertTrue(
            NotificationPreference.objects.filter(
                user=user2, notification_type=notification_type
            ).exists()
        )

    def test_create_default_notification_preferences_signal_disconnected(self):
        notification_type = NotificationType.objects.create(name="TOP_PRIORITIES")
        user = User.objects.create_user(username="user", password="user123")
        self.assertEqual(NotificationPreference.objects.filter(user=user).count(), 0)

    def test_update_notification_type_for_all_users_signal_disconnected(self):
        user = User.objects.create_user(username="user", password="user123")
        notification_type = NotificationType.objects.create(name="TOP_PRIORITIES")
        self.assertEqual(
            NotificationPreference.objects.filter(notification_type=notification_type).count(), 0
        )
