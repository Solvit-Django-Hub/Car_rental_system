from rest_framework import serializers
from .models import Rental, Payment, Review


class RentalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rental
        fields = [
            "id",
            "user",
            "car",
            "start_date",
            "end_date",
            "total_price",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "total_price",
            "created_at",
        ]

    def validate(self, data):
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError(
                "End date cannot be before start date."
            )

        return data

    def create(self, validated_data):
        car = validated_data["car"]
        start_date = validated_data["start_date"]
        end_date = validated_data["end_date"]

        rental_days = (end_date - start_date).days

        if rental_days <= 0:
            raise serializers.ValidationError(
                "Rental period must be at least one day."
            )

        total_price = rental_days * car.price_per_day

        validated_data["total_price"] = total_price

        return super().create(validated_data)
    
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "rental",
            "amount",
            "payment_method",
            "payment_date",
            "status",
        ]
        read_only_fields = [
            "id",
            "amount",
            "payment_date",
        ]

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Payment amount cannot be negative."
            )
        return value

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "car",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
        ]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Rating must be between 1 and 5."
            )
        return value