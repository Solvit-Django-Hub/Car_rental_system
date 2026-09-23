from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken, TokenError



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

class ProfileUpdateSerializer(serializers.ModelSerializer):

    old_password = serializers.CharField(
        write_only=True,
        required=False
    )

    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        required=False,
        validators=[validate_password]
    )

    new_password2 = serializers.CharField(
        write_only=True,
        required=False
    )

    class Meta:
        model = User
        fields = [
            "name",
            "email",
            "old_password",
            "new_password",
            "new_password2",
        ]

    def validate_email(self, value):
        user = self.instance

        if User.objects.exclude(
            user_id=user.user_id
        ).filter(
            email=value
        ).exists():

            raise serializers.ValidationError(
                "This email is already in use."
            )

        return value

    def validate(self, data):

        old_password = data.get("old_password")
        new_password = data.get("new_password")
        new_password2 = data.get("new_password2")

        # Password change validation
        if new_password and not old_password:
            raise serializers.ValidationError({
                "old_password": "Old password is required."
            })

        if old_password and not new_password:
            raise serializers.ValidationError({
                "new_password": "New password is required."
            })

        if new_password and new_password != new_password2:
            raise serializers.ValidationError({
                "new_password2": "New passwords do not match."
            })

        if old_password and not self.instance.check_password(
            old_password
        ):
            raise serializers.ValidationError({
                "old_password": "Old password is incorrect."
            })

        if old_password and new_password:
            if old_password == new_password:
                raise serializers.ValidationError({
                    "new_password": "New password must be different from the old password."
                })

        return data

    def update(self, instance, validated_data):

        old_password = validated_data.pop(
            "old_password",
            None
        )

        new_password = validated_data.pop(
            "new_password",
            None
        )

        validated_data.pop(
            "new_password2",
            None
        )

        instance.name = validated_data.get(
            "name",
            instance.name
        )

        instance.email = validated_data.get(
            "email",
            instance.email
        )

        if new_password:
            instance.set_password(new_password)

        instance.save()

        return instance

class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "user_id",
            "name",
            "email",
            "role",
            "is_active",
        ]