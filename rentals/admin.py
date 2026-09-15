from django.contrib import admin
from .models import Rental, Payment, Review


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "car",
        "start_date",
        "end_date",
        "total_price",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "start_date",
        "end_date",
    )

    search_fields = (
        "user__name",
        "user__email",
        "car__brand",
        "car__model",
        "car__registration_number",
    )

    ordering = (
        "-created_at",
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "rental",
        "amount",
        "payment_method",
        "payment_date",
        "status",
    )

    list_filter = (
        "payment_method",
        "status",
    )

    search_fields = (
        "rental__user__name",
        "rental__user__email",
    )

    ordering = (
        "-payment_date",
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "car",
        "rating",
        "created_at",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    search_fields = (
        "user__name",
        "user__email",
        "car__brand",
        "car__model",
        "comment",
    )

    ordering = (
        "-created_at",
    )