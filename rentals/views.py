from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Rental, Payment, Review
from .serializers import RentalSerializer, PaymentSerializer,ReviewSerializer
from accounts.views import IsAdminOrManager


class RentalListCreateView(generics.ListCreateAPIView):
    serializer_class = RentalSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]

    filterset_fields = [
        "car",
        "status",
        "start_date",
        "end_date",
    ]

    search_fields = [
        "car__brand",
        "car__model",
        "user__name",
        "user__email",
    ]

    ordering_fields = [
        "start_date",
        "end_date",
        "total_price",
        "created_at",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user

        if user.role in ["admin", "manager"]:
            return Rental.objects.all()

        return Rental.objects.filter(user=user)

    def get_permissions(self):
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RentalDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RentalSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role in ["admin", "manager"]:
            return Rental.objects.all()

        return Rental.objects.filter(user=user)

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminOrManager()]

        return [IsAuthenticated()]

class PaymentListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role in ["admin", "manager"]:
            return Payment.objects.all()

        return Payment.objects.filter(rental__user=user)

    def get_permissions(self):
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        rental_id = self.request.data.get("rental")

        try:
            rental = Rental.objects.get(id=rental_id)
        except Rental.DoesNotExist:
            raise serializers.ValidationError(
                {"rental": "Rental does not exist."}
            )

        # Customers can only create payments for their own rentals
        if (
            self.request.user.role not in ["admin", "manager"]
            and rental.user != self.request.user
        ):
            raise PermissionDenied(
                "You can only make payments for your own rentals."
            )

        serializer.save(
            amount=rental.total_price
        )


class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role in ["admin", "manager"]:
            return Payment.objects.all()

        return Payment.objects.filter(rental__user=user)

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminOrManager()]

        return [IsAuthenticated()]

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.all()

    def get_permissions(self):
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.all()

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated()]

        return [IsAuthenticated()]

    def perform_update(self, serializer):
        review = self.get_object()

        if (
            self.request.user != review.user
            and self.request.user.role not in ["admin", "manager"]
        ):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "You can only update your own review."
            )

        serializer.save()

    def perform_destroy(self, instance):
        if (
            self.request.user != instance.user
            and self.request.user.role not in ["admin", "manager"]
        ):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(
                "You can only delete your own review."
            )

        instance.delete()