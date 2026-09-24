from datetime import date

from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import User
from cars.models import Category, Car
from .models import Rental, Payment, Review


class RentalAPITests(APITestCase):

    def setUp(self):
        self.customer = User.objects.create_user(
            email="customer@test.com",
            name="Customer",
            password="TestPassword123",
            role="customer"
        )

        self.manager = User.objects.create_user(
            email="manager@test.com",
            name="Manager",
            password="TestPassword123",
            role="manager"
        )

        self.category = Category.objects.create(name="SUV")

        self.car = Car.objects.create(
            category=self.category,
            brand="Toyota",
            model="RAV4",
            year=2023,
            registration_number="RAB123A",
            price_per_day=50000,
            available=True
        )

    def test_customer_can_create_rental(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            "/api/rentals/rentals/",
            {
                "car": self.car.id,
                "start_date": "2026-09-20",
                "end_date": "2026-09-22",
                "status": "pending"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            float(response.data["total_price"]),
            100000
        )

    def test_invalid_rental_dates_are_rejected(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            "/api/rentals/rentals/",
            {
                "car": self.car.id,
                "start_date": "2026-09-25",
                "end_date": "2026-09-20",
                "status": "pending"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_customer_can_only_view_own_rentals(self):
        Rental.objects.create(
            user=self.manager,
            car=self.car,
            start_date=date(2026, 9, 20),
            end_date=date(2026, 9, 22),
            total_price=100000
        )

        self.client.force_authenticate(user=self.customer)

        response = self.client.get("/api/rentals/rentals/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)


class PaymentAPITests(APITestCase):

    def setUp(self):
        self.customer = User.objects.create_user(
            email="customer@test.com",
            name="Customer",
            password="TestPassword123",
            role="customer"
        )

        self.category = Category.objects.create(name="Sedan")

        self.car = Car.objects.create(
            category=self.category,
            brand="Toyota",
            model="Corolla",
            year=2023,
            registration_number="RAC456B",
            price_per_day=40000,
            available=True
        )

        self.rental = Rental.objects.create(
            user=self.customer,
            car=self.car,
            start_date=date(2026, 9, 20),
            end_date=date(2026, 9, 22),
            total_price=80000
        )

    def test_customer_can_make_payment_for_own_rental(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            "/api/rentals/payments/",
            {
                "rental": self.rental.id,
                "payment_method": "cash",
                "status": "completed"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            float(response.data["amount"]),
            80000
        )


class ReviewAPITests(APITestCase):

    def setUp(self):
        self.customer = User.objects.create_user(
            email="customer@test.com",
            name="Customer",
            password="TestPassword123",
            role="customer"
        )

        self.category = Category.objects.create(name="Luxury")

        self.car = Car.objects.create(
            category=self.category,
            brand="BMW",
            model="X5",
            year=2024,
            registration_number="RAD789C",
            price_per_day=100000,
            available=True
        )

    def test_customer_can_create_review(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            "/api/rentals/reviews/",
            {
                "car": self.car.id,
                "rating": 5,
                "comment": "Excellent car!"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_invalid_rating_is_rejected(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.post(
            "/api/rentals/reviews/",
            {
                "car": self.car.id,
                "rating": 6,
                "comment": "Invalid rating"
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )