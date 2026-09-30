from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, LoginSerializer, LogoutSerializer,ProfileUpdateSerializer,UserListSerializer,ActivateAccountSerializer,ResetPasswordSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .utils import generate_otp


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        send_mail(
            subject="Car Rental System - Account Activation OTP",
            message=(
                f"Hello {user.name},\n\n"
                f"Thank you for registering with the Car Rental System.\n\n"
                f"Your account activation OTP is:\n\n"
                f"{user.otp}\n\n"
                f"This OTP will expire in 10 minutes.\n\n"
                f"Please do not share this OTP with anyone."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return Response(
            {
                "message": (
                    "Account created successfully. "
                    "Please check your email for the OTP "
                    "and activate your account before logging in."
                ),
                "email": user.email,
            },
            status=status.HTTP_201_CREATED
        )

class ActivateAccountView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ActivateAccountSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_active:
            return Response(
                {"message": "Account is already activated."},
                status=status.HTTP_200_OK
            )

        if user.otp_purpose != "activation":
            return Response(
                {"error": "Invalid activation OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.otp != otp:
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.otp_created_at:
            return Response(
                {"error": "OTP is invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > user.otp_created_at + timedelta(minutes=10):
            return Response(
                {"error": "OTP has expired. Please request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Activate account
        user.is_active = True

        # Clear OTP after successful activation
        user.otp = None
        user.otp_created_at = None
        user.otp_purpose = None

        user.save()

        return Response(
            {
                "message": (
                    "Account activated successfully. "
                    "You can now log in."
                )
            },
            status=status.HTTP_200_OK
        )

class ResendActivationOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_active:
            return Response(
                {"message": "Account is already activated."},
                status=status.HTTP_200_OK
            )

        new_otp = generate_otp()

        user.otp = new_otp
        user.otp_created_at = timezone.now()
        user.otp_purpose = "activation"
        user.save()

        send_mail(
            subject="Car Rental System - New Account Activation OTP",
            message=(
                f"Hello {user.name},\n\n"
                f"Your new account activation OTP is:\n\n"
                f"{new_otp}\n\n"
                f"This OTP will expire in 10 minutes.\n\n"
                f"Please do not share this OTP with anyone."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return Response(
            {
                "message": (
                    "A new activation OTP has been sent "
                    "to your email."
                )
            },
            status=status.HTTP_200_OK
        )

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response(
                {
                    "message": (
                        "If an account exists with this email, "
                        "a password reset OTP has been sent."
                    )
                },
                status=status.HTTP_200_OK
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {
                    "message": (
                        "If an account exists with this email, "
                        "a password reset OTP has been sent."
                    )
                },
                status=status.HTTP_200_OK
            )

        if not user.is_active:
            return Response(
                {
                    "message": (
                        "If an account exists with this email, "
                        "a password reset OTP has been sent."
                    )
                },
                status=status.HTTP_200_OK
            )

        otp = generate_otp()

        user.otp = otp
        user.otp_created_at = timezone.now()
        user.otp_purpose = "password_reset"
        user.save()

        send_mail(
            subject="Car Rental System - Password Reset OTP",
            message=(
                f"Hello {user.name},\n\n"
                f"We received a request to reset your password.\n\n"
                f"Your password reset OTP is:\n\n"
                f"{otp}\n\n"
                f"This OTP will expire in 10 minutes.\n\n"
                f"If you did not request a password reset, "
                f"please ignore this email.\n\n"
                f"Please do not share this OTP with anyone."
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return Response(
            {
                "message": (
                    "If an account exists with this email, "
                    "a password reset OTP has been sent."
                )
            },
            status=status.HTTP_200_OK
        )
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_active:
            return Response(
                {"error": "Invalid email or OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.otp_purpose != "password_reset":
            return Response(
                {"error": "Invalid password reset OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.otp != otp:
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.otp_created_at:
            return Response(
                {"error": "OTP is invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > user.otp_created_at + timedelta(minutes=10):
            return Response(
                {"error": "OTP has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)

        user.otp = None
        user.otp_created_at = None
        user.otp_purpose = None

        user.save()

        return Response(
            {
                "message": (
                    "Password reset successfully. "
                    "You can now log in with your new password."
                )
            },
            status=status.HTTP_200_OK
        )

class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid email or OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_active:
            return Response(
                {"error": "Invalid email or OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.otp_purpose != "password_reset":
            return Response(
                {"error": "Invalid password reset OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.otp != otp:
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.otp_created_at:
            return Response(
                {"error": "OTP is invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if timezone.now() > user.otp_created_at + timedelta(minutes=10):
            return Response(
                {"error": "OTP has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)

        user.otp = None
        user.otp_created_at = None
        user.otp_purpose = None

        user.save()

        return Response(
            {
                "message": (
                    "Password reset successfully. "
                    "You can now log in with your new password."
                )
            },
            status=status.HTTP_200_OK
        )

class LoginView(generics.GenericAPIView):

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data["user"]

        return Response({
            "message": "Login successful.",

            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
            },

            "tokens": {
                "access": serializer.validated_data["access"],
                "refresh": serializer.validated_data["refresh"],
            }
        })
class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        return Response({
            "user_id": user.user_id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
        })

class LogoutView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        serializer = LogoutSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response({
            "message": "Logout successful."
        })


class ProfileUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):

        user = request.user

        serializer = ProfileUpdateSerializer(
            user,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response({
            "message": "Account updated successfully.",
            "user": {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
            }
        }, status=status.HTTP_200_OK)

class IsAdminOrManager(BasePermission):

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and request.user.role in ["admin", "manager"]
        )

class UserListView(generics.ListAPIView):

    queryset = User.objects.all().order_by("user_id")
    serializer_class = UserListSerializer
    permission_classes = [IsAdminOrManager]