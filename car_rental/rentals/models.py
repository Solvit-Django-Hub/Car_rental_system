# rentals/models.py
from django.db import models
from django.conf import settings
from vehicles.models import Vehicle

class Rental(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rentals')
vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='rentals')
    start_date = models.DateField()
    end_date = models.DateField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Rental #{self.id} - {self.customer.username}"

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('card', 'Credit/Debit Card'),
        ('cash', 'Cash'),
        ('mobile_money', 'Mobile Money'),
    )
    rental = models.OneToOneField(Rental, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    is_successful = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment for Rental #{self.rental.id}"