from django.db import models
from django.core.validators import MinValueValidator


class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    def __str__(self):
        return self.name


class Car(models.Model):

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="cars"
    )

    brand = models.CharField(
        max_length=100
    )

    model = models.CharField(
        max_length=100
    )

    year = models.PositiveIntegerField()

    registration_number = models.CharField(
        max_length=20,
        unique=True
    )

    price_per_day = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    available = models.BooleanField(
        default=True
    )

    def __str__(self):
        return f"{self.brand} {self.model} ({self.registration_number})"