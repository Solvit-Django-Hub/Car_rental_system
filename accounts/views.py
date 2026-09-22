from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserRegistrationSerializer, LoginSerializer, LogoutSerializer,ProfileUpdateSerializer,UserListSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import User


class UserRegistrationView(generics.CreateAPIView):

    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


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

    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdminOrManager]