
from django.urls import path
from userauth import views as userauth_views

urlpatterns = [
     # Example endpoints
     
     path('register/', userauth_views.ReagistrationUserAPIView.as_view(), name='user-register'),
     path('login/', userauth_views.LoginUserAPIView.as_view(), name='user-login'),
     path("reset-password/", userauth_views.RequistPasswordResetAPIView.as_view(), name="reset-password"),
     path("verify-otp/", userauth_views.ResetOtpVerifyAPIView.as_view(), name="verify-otp"),
     path("confirm-reset-password/", userauth_views.PasswordResetConfirmAPIView.as_view(), name="confirm-reset-password"),
     path("profile/", userauth_views.UserProfileAPIView.as_view(), name="user-profile"),
     
]
