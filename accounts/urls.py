from django.urls import path
from .views import ProfileUpdateView, UserRegistrationView, LoginView, MeView, LogoutView,UserListView,ActivateAccountView,ResendActivationOTPView,ForgotPasswordView,ResetPasswordView


urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", MeView.as_view(), name="me"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile/", ProfileUpdateView.as_view(), name="profile-update"),
    path("users/",UserListView.as_view(),name="user-list"),
    path("activate/",ActivateAccountView.as_view(),name="activate-account"),
    path("resend-otp/",ResendActivationOTPView.as_view(),name="resend-activation-otp"),
    path("forgot-password/",ForgotPasswordView.as_view(),name="forgot-password"),
    path("reset-password/",ResetPasswordView.as_view(),name="reset-password"),
]