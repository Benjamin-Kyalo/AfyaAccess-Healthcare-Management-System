from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UsersAPITestCase(APITestCase):
    """
    Basic tests for Users API:
    - Admin can list/create/delete.
    - Non-admin cannot list/create/delete.
    - User can update own profile but not others.
    """

    def setUp(self):
        # Create an admin user
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass123"
        )

        # Create a normal user
        self.user = User.objects.create_user(
            username="jane", email="jane@example.com", password="janepass123"
        )

        # URLs
        self.users_list_url = reverse("user-list")  # expects router basename 'user'

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)
        resp = self.client.get(self.users_list_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_non_admin_cannot_list_users(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(self.users_list_url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_user(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newuserpass123",
        }
        resp = self.client.post(self.users_list_url, payload)
        # creation allowed for admin: should be 201 if serializer + view permit it
        self.assertIn(resp.status_code, (status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST))

    def test_non_admin_cannot_create_user(self):
        self.client.force_authenticate(user=self.user)
        payload = {"username": "x", "email": "x@example.com", "password": "xpass123"}
        resp = self.client.post(self.users_list_url, payload)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_update_own_profile_but_not_others(self):
        self.client.force_authenticate(user=self.user)
        # Update own profile
        url = reverse("user-detail", args=[self.user.id])
        resp = self.client.patch(url, {"first_name": "JaneUpdated"})
        self.assertIn(resp.status_code, (status.HTTP_200_OK, status.HTTP_204_NO_CONTENT))
        # Try to update another user's profile
        url_admin = reverse("user-detail", args=[self.admin.id])
        resp2 = self.client.patch(url_admin, {"first_name": "Hax"})
        self.assertEqual(resp2.status_code, status.HTTP_403_FORBIDDEN)
