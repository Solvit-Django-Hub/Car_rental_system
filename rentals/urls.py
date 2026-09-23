from django.urls import path

from .views import (
    RentalListCreateView,
    RentalDetailView,
    PaymentListCreateView,
    PaymentDetailView,
    ReviewListCreateView,
    ReviewDetailView,
)

urlpatterns = [
    path(
        "rentals/",
        RentalListCreateView.as_view(),
        name="rental-list-create"
    ),
    path(
        "rentals/<int:pk>/",
        RentalDetailView.as_view(),
        name="rental-detail"
    ),
    path(
    "payments/",
    PaymentListCreateView.as_view(),
    name="payment-list-create"
),
path(
    "payments/<int:pk>/",
    PaymentDetailView.as_view(),
    name="payment-detail"
),
path(
    "reviews/",
    ReviewListCreateView.as_view(),
    name="review-list-create"
),
path(
    "reviews/<int:pk>/",
    ReviewDetailView.as_view(),
    name="review-detail"
),
]