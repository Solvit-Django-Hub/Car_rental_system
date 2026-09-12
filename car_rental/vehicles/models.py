# vehicles/models.py
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Vehicle(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='vehicles')
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    license_plate = models.CharField(max_length=20, unique=True)
    daily_rate = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.make} {self.model} ({self.license_plate})"