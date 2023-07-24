from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/", views.RegisterBranch.as_view(), name="register"),
    path("reset_password/", views.SendOTP.as_view(), name="reset_password"),
    path("otp_verification/", views.OTPVerification.as_view(), name="otp_verification"),
    path("new_password/", views.NewPassword.as_view(), name="new_password"),
    path("resend_otp/", views.resend_otp, name="resend_otp"),
    path("change_password/", views.ChangePassword.as_view(), name="change_password"),
]
