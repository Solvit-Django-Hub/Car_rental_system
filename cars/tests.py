from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import User
from .models import Category, Car


class CarAPITests(APITestCase):

    def setUp(self):
        self.manager = User.objects.create_user(
            email="manager@test.com",
            name="Manager",
            password="TestPassword123",
            role="manager"
        )

        self.customer = User.objects.create_user(
            email="customer@test.com",
            name="Customer",
            password="TestPassword123",
            role="customer"
        )

        self.category = Category.objects.create(
            name="SUV",
            description="SUV cars"
        )

        self.car = Car.objects.create(
            category=self.category,
            brand="Toyota",
            model="RAV4",
            year=2023,
            registration_number="RAB123A",
            price_per_day=50000,
            available=True
        )

    def test_authenticated_user_can_view_cars(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get("/api/cars/cars/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_can_create_car(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            "/api/cars/cars/",
            {
                "category": self.category.id,
                "brand": "Honda",
                "model": "CR-V",
                "year": 2024,
                "registration_number": "RAC456B",
                "price_per_day": 60000,
                "available": True
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_customer_cannot_create_car(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            "/api/cars/cars/",
            {
                "category": self.category.id,
                "brand": "Honda",
                "model": "CR-V",
                "year": 2024,
                "registration_number": "RAC456B",
                "price_per_day": 60000,
                "available": True
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN
        )

    def test_negative_price_is_rejected(self):
        self.client.force_authenticate(user=self.manager)

        response = self.client.post(
            "/api/cars/cars/",
            {
                "category": self.category.id,
                "brand": "Honda",
                "model": "CR-V",
                "year": 2024,
                "registration_number": "RAD789C",
                "price_per_day": -1000,
                "available": True
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )