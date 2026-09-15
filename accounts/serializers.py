from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .models import Profile


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    password2 = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = [
            "user_id",
            "name",
            "email",
            "password",
            "password2",
            "role",
        ]
        read_only_fields = ["user_id"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Passwords do not match."}
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data
        )

        return user

class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        if not user.check_password(password):
            raise serializers.ValidationError(
                "Invalid email or password."
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "This account is inactive."
            )

        refresh = RefreshToken.for_user(user)

        attrs["user"] = user
        attrs["refresh"] = str(refresh)
        attrs["access"] = str(refresh.access_token)

        return attrs

class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField()

    def validate(self, attrs):
        try:
            self.token = RefreshToken(attrs["refresh"])
        except TokenError:
            raise serializers.ValidationError({
                "refresh": "Invalid or expired refresh token."
            })

        return attrs

    def save(self, **kwargs):
        self.token.blacklist()