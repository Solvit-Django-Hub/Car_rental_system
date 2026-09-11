from django.contrib import admin
from .models import Rental, Payment

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'vehicle', 'start_date', 'end_date', 'total_cost', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('customer__username', 'vehicle__license_plate')
    list_editable = ('status',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'rental', 'amount', 'payment_method', 'is_successful', 'payment_date')
    list_filter = ('is_successful', 'payment_method', 'payment_date')
    search_fields = ('rental__id', 'rental__customer__username')