from django.urls import path
from .views import ProfileUpdateView, UserRegistrationView, LoginView, MeView, LogoutView,UserListView


urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileUpdateView.as_view(), name="profile-update"),
    path("users/",UserListView.as_view(),name="user-list"),
]