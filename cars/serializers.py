from rest_framework import serializers
from .models import Category, Car


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "description",
        ]

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Category name cannot be empty."
            )
        return value
    



class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = [
            "id",
            "category",
            "brand",
            "model",
            "year",
            "registration_number",
            "price_per_day",
            "available",
        ]

    def validate_price_per_day(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Price per day cannot be negative."
            )
        return value

    def validate_registration_number(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Registration number cannot be empty."
            )
        return value