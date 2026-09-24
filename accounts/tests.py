from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .models import User


class AuthenticationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="customer@test.com",
            name="Test Customer",
            password="TestPassword123"
        )

    def test_login_success(self):
        response = self.client.post(
            "/api/accounts/login/",
            {
                "email": "customer@test.com",
                "password": "TestPassword123"
            }
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)

    def test_login_invalid_password(self):
        response = self.client.post(
            "/api/accounts/login/",
            {
                "email": "customer@test.com",
                "password": "WrongPassword123"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_protected_endpoint_requires_authentication(self):
        response = self.client.get("/api/accounts/me/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )


class UserPermissionTests(APITestCase):

    def setUp(self):
        self.customer = User.objects.create_user(
            email="customer@test.com",
            name="Customer",
            password="TestPassword123",
            role="customer"
        )

        self.manager = User.objects.create_user(
            email="manager@test.com",
            name="Manager",
            password="TestPassword123",
            role="manager"
        )

    def test_customer_cannot_view_all_users(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get("/api/accounts/users/")

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_manager_can_view_all_users(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.get("/api/accounts/users/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )