from datetime import date

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from accounts.models import User
from vehicles.models import Category, Vehicle
from .models import Rental


class RentalValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='customer1',
            password='testpass123',
            email='customer1@example.com',
        )
        category = Category.objects.create(name='SUV')
        self.vehicle = Vehicle.objects.create(
            category=category,
            make='Toyota',
            model='RAV4',
            year=2024,
            license_plate='TEST-001',
            daily_rate=100.00,
        )

    def test_model_validation_rejects_end_date_before_start_date(self):
        rental = Rental(
            customer=self.user,
            vehicle=self.vehicle,
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 9),
            total_cost=100.00,
            status='pending',
        )

        with self.assertRaisesMessage(ValidationError, 'End date must be on or after start date.'):
            rental.full_clean()

    def test_database_constraint_rejects_invalid_date_order(self):
        with self.assertRaises(IntegrityError):
            Rental.objects.bulk_create(
                [
                    Rental(
                        customer=self.user,
                        vehicle=self.vehicle,
                        start_date=date(2026, 9, 10),
                        end_date=date(2026, 9, 9),
                        total_cost=100.00,
                        status='pending',
                    )
                ]
            )
