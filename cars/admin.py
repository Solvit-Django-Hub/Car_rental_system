from django.contrib import admin
from .models import Category, Car


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "description",
    )

    search_fields = (
        "name",
    )


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "brand",
        "model",
        "year",
        "registration_number",
        "category",
        "price_per_day",
        "available",
    )

    list_filter = (
        "category",
        "available",
        "year",
    )

    search_fields = (
        "brand",
        "model",
        "registration_number",
    )

    ordering = (
        "brand",
        "model",
    )