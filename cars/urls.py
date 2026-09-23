from django.urls import path

from .views import (
    CategoryListCreateView,
    CategoryDetailView, CarListCreateView, CarDetailView
)

urlpatterns = [
    path(
        "categories/",
        CategoryListCreateView.as_view(),
        name="category-list-create"
    ),
    path(
        "categories/<int:pk>/",
        CategoryDetailView.as_view(),
        name="category-detail"
    ),
    path(
    "cars/",
    CarListCreateView.as_view(),
    name="car-list-create"
),
path(
    "cars/<int:pk>/",
    CarDetailView.as_view(),
    name="car-detail"
),
]