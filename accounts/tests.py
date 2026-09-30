from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthenticationTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="customer@test.com",
            name="Test Customer",
            password="TestPassword123"
        )

    def test_login_success(self):
        self.user.is_active = True
        self.user.save()

        response = self.client.post(
            "/api/accounts/login/",
            {
                "email": "customer@test.com",
                "password": "TestPassword123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertIn("tokens", response.data)

    def test_login_invalid_password(self):
        response = self.client.post(
            "/api/accounts/login/",
            {
                "email": "customer@test.com",
                "password": "WrongPassword123"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_protected_endpoint_requires_authentication(self):
        response = self.client.get(
            "/api/accounts/me/"
        )

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
        self.client.force_authenticate(
            user=self.customer
        )

        response = self.client.get(
            "/api/accounts/users/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_manager_can_view_all_users(self):
        self.client.force_authenticate(
            user=self.manager
        )

        response = self.client.get(
            "/api/accounts/users/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


class AccountActivationTests(APITestCase):

    def setUp(self):
        self.email = "activation@example.com"
        self.password = "StrongPassword123!"

        self.user = get_user_model().objects.create_user(
            email=self.email,
            name="Activation User",
            password=self.password,
            role="customer"
        )

        self.user.is_active = False
        self.user.otp = "123456"
        self.user.otp_created_at = timezone.now()
        self.user.otp_purpose = "activation"
        self.user.save()

    def test_activate_account_with_correct_otp(self):
        response = self.client.post(
            "/api/accounts/activate/",
            {
                "email": self.email,
                "otp": "123456"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.user.refresh_from_db()

        self.assertTrue(self.user.is_active)
        self.assertIsNone(self.user.otp)
        self.assertIsNone(self.user.otp_created_at)
        self.assertIsNone(self.user.otp_purpose)

    def test_activate_account_with_wrong_otp(self):
        response = self.client.post(
            "/api/accounts/activate/",
            {
                "email": self.email,
                "otp": "000000"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.user.refresh_from_db()

        self.assertFalse(self.user.is_active)

    def test_activate_account_with_expired_otp(self):
        self.user.otp_created_at = (
            timezone.now() - timedelta(minutes=11)
        )
        self.user.save()

        response = self.client.post(
            "/api/accounts/activate/",
            {
                "email": self.email,
                "otp": "123456"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.user.refresh_from_db()

        self.assertFalse(self.user.is_active)

    @patch("accounts.views.send_mail")
    def test_resend_activation_otp(self, mock_send_mail):
        response = self.client.post(
            "/api/accounts/resend-otp/",
            {
                "email": self.email
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.user.refresh_from_db()

        self.assertIsNotNone(self.user.otp)
        self.assertEqual(
            len(self.user.otp),
            6
        )
        self.assertEqual(
            self.user.otp_purpose,
            "activation"
        )

        mock_send_mail.assert_called_once()

    def test_activated_account_cannot_use_activation_otp_again(self):
        self.user.is_active = True
        self.user.save()

        response = self.client.post(
            "/api/accounts/activate/",
            {
                "email": self.email,
                "otp": "123456"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )


class PasswordResetTests(APITestCase):

    def setUp(self):
        self.email = "reset@example.com"
        self.password = "OldPassword123!"

        self.user = get_user_model().objects.create_user(
            email=self.email,
            name="Reset User",
            password=self.password,
            role="customer"
        )

        self.user.is_active = True
        self.user.otp = "654321"
        self.user.otp_created_at = timezone.now()
        self.user.otp_purpose = "password_reset"
        self.user.save()

    def test_reset_password_with_correct_otp(self):
        response = self.client.post(
            "/api/accounts/reset-password/",
            {
                "email": self.email,
                "otp": "654321",
                "new_password": "NewPassword123!",
                "new_password2": "NewPassword123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                "NewPassword123!"
            )
        )

        self.assertIsNone(self.user.otp)
        self.assertIsNone(
            self.user.otp_created_at
        )
        self.assertIsNone(
            self.user.otp_purpose
        )

    def test_reset_password_with_wrong_otp(self):
        response = self.client.post(
            "/api/accounts/reset-password/",
            {
                "email": self.email,
                "otp": "000000",
                "new_password": "NewPassword123!",
                "new_password2": "NewPassword123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                self.password
            )
        )

    def test_reset_password_with_expired_otp(self):
        self.user.otp_created_at = (
            timezone.now() - timedelta(minutes=11)
        )
        self.user.save()

        response = self.client.post(
            "/api/accounts/reset-password/",
            {
                "email": self.email,
                "otp": "654321",
                "new_password": "NewPassword123!",
                "new_password2": "NewPassword123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                self.password
            )
        )

    def test_reset_password_with_mismatched_passwords(self):
        response = self.client.post(
            "/api/accounts/reset-password/",
            {
                "email": self.email,
                "otp": "654321",
                "new_password": "NewPassword123!",
                "new_password2": "DifferentPassword123!"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.user.refresh_from_db()

        self.assertTrue(
            self.user.check_password(
                self.password
            )
        )

    @patch("accounts.views.send_mail")
    def test_forgot_password_existing_email(
        self,
        mock_send_mail
    ):
        response = self.client.post(
            "/api/accounts/forgot-password/",
            {
                "email": self.email
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            "If an account exists with this email",
            response.data["message"]
        )

        self.user.refresh_from_db()

        self.assertIsNotNone(
            self.user.otp
        )

        self.assertEqual(
            len(self.user.otp),
            6
        )

        self.assertEqual(
            self.user.otp_purpose,
            "password_reset"
        )

        self.assertIsNotNone(
            self.user.otp_created_at
        )

        mock_send_mail.assert_called_once()

    @patch("accounts.views.send_mail")
    def test_forgot_password_non_existing_email(
        self,
        mock_send_mail
    ):
        response = self.client.post(
            "/api/accounts/forgot-password/",
            {
                "email": "doesnotexist@example.com"
            },
            format="json"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            "If an account exists with this email",
            response.data["message"]
        )

        mock_send_mail.assert_not_called()
