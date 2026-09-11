from django.contrib import admin
from .models import Category, Vehicle

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'license_plate', 'daily_rate', 'is_available', 'category')
    list_filter = ('is_available', 'category', 'year')
    search_fields = ('make', 'model', 'license_plate')
    list_editable = ('is_available', 'daily_rate')