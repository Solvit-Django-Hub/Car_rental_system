from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import UserRegistrationSerializer, LoginSerializer, LogoutSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

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