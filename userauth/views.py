from django.shortcuts import render
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework import generics, permissions, response,status
from .serializers import UserSerializer,LoginSerializer ,PasswordResetRequestSerializer,ResetOtpSerializer,PasswordResetConfirmSerializer,UserProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
import random
from rest_framework.response import Response
from .models import User
from rest_framework import parsers
from datetime import timedelta
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.

user=get_user_model()


def send_otp_email(email, otp):
    send_mail(
        subject="Your OTP Code",
        message=f"Your OTP code is {otp}",
        from_email="no-reply@example.com",
        recipient_list=[email],
        fail_silently=False,
    )


def is_otp_expired(otp_created_time,minutes=5):
     if otp_created_time is None:
          return True
     return otp_created_time < timezone.now() - timedelta(minutes=minutes)


# ---------------- USER REGISTRATION VIEW ---------------- #
class ReagistrationUserAPIView(generics.CreateAPIView):
     queryset = user.objects.all()
     serializer_class=UserSerializer
     permission_classes = [permissions.AllowAny]

     def post(self, request, *args, **kwargs):
          email = request.data.get("email")
          name = request.data.get("name")
          phone = request.data.get("phone")
          role = request.data.get("role")
          password = request.data.get("password")

          if not email or not name or not phone or not role or not password:
               return response.Response(
                    {"error": "All fields are required."},
                    status=status.HTTP_400_BAD_REQUEST,
               )

          if user.objects.filter(email=email).exists():
               return response.Response(
                    {"error": "Email already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
               )

          new_user = user.objects.create_user(
               email=email,
               name=name,
               phone=phone,
               role=role,
               password=password,
          )

          return response.Response(
               {
                    
                    "id": new_user.id,
                    "email": new_user.email,
                    "name": new_user.name,
                    "phone": new_user.phone,
                    "role": new_user.role,
                    "message": "User registered successfully."
                    
                    },
               status=status.HTTP_201_CREATED,
          )

# ---------------- USER LOGIN VIEW ---------------- #
class LoginUserAPIView(generics.GenericAPIView):
     serializer_class = LoginSerializer
     permission_classes = [permissions.AllowAny]

     def post(self, request, *args, **kwargs):
          email = request.data.get("email")
          password = request.data.get("password")

          if not email or not password:
               return response.Response(
                    {"error": "Email and password are required."},
                    status=status.HTTP_400_BAD_REQUEST,
               )

          user_instance = authenticate(request, email=email, password=password)

          if user_instance is None:
               return response.Response(
                    {"error": "Invalid email or password."},
                    status=status.HTTP_401_UNAUTHORIZED,
               )
          refresh_token = RefreshToken.for_user(user_instance)
          return response.Response(
               {
                    # "id": user_instance.id,
                    # "email": user_instance.email,
                    # "name": user_instance.name,
                    # "phone": user_instance.phone,
                    # "role": user_instance.role,
                    "access": str(refresh_token.access_token),
                    "refresh": str(refresh_token),
                    "message": "User Login successful."
                    
                    
                    },
               status=status.HTTP_200_OK,
          )


class RequistPasswordResetAPIView(generics.GenericAPIView):
     serializer_class = PasswordResetRequestSerializer
     permission_classes = [permissions.AllowAny]

     def post(self, request, *args, **kwargs):
          email = request.data.get("email")

          if not email:
               return response.Response(
                    {"error": "Email is required."},
                    status=status.HTTP_400_BAD_REQUEST,
               )

          try:
               user_instance = user.objects.get(email=email)
          except user.DoesNotExist:
               return response.Response(
                    {"error": "User with this email does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
               )

          otp = str(random.randint(1000, 9999))
          user_instance.password_reset_otp = otp
          user_instance.password_reset_otp_created_at = timezone.now()
          user_instance.save(update_fields=["password_reset_otp", "password_reset_otp_created_at"])

          send_otp_email(email, otp)

          return response.Response(
               {"message": "OTP has been sent to your email."},
               status=status.HTTP_200_OK,
          )
          
          
class ResetOtpVerifyAPIView(generics.GenericAPIView):
    serializer_class = ResetOtpSerializer
    permission_classes = [permissions.AllowAny]

    def _verify_password_reset_otp(self, user):
        if is_otp_expired(user.password_reset_otp_created_at):
            return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # OTP যাচাই করা হলে
        user.password_reset_token  = True
        user.password_reset_otp = None
        user.password_reset_otp_created_at = None
        user.save(update_fields=["password_reset_token", "password_reset_otp", "password_reset_otp_created_at"])

        return Response(
            {"message": "OTP has been successfully verified. You can now reset your password."},
            status=status.HTTP_200_OK
        )

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        if not email or not otp:
            return Response({"error": "Email and OTP are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, password_reset_otp=otp)
            return self._verify_password_reset_otp(user)
        except User.DoesNotExist:
            return Response({"error": "Invalid OTP Or Email"}, status=status.HTTP_400_BAD_REQUEST)
       
class PasswordResetConfirmAPIView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")

        if not email or not new_password:
            return Response({"error": "Email and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            if not user.password_reset_token:
                return Response({"error": "Password reset token is invalid or has not been generated."}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.password_reset_token = None
            user.save(update_fields=["password", "password_reset_token"])

            return Response({"message": "Password has been successfully reset."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)
       
       
class UserProfileAPIView(generics.RetrieveUpdateAPIView):
     serializer_class = UserProfileSerializer
     permission_classes = [permissions.IsAuthenticated]
     parser_classes = [parsers.MultiPartParser, parsers.FormParser]

     def get_object(self):
          return self.request.user.profile
     
     def update(self, request, *args, **kwargs):
          partial = kwargs.pop('partial', False)
          instance = self.get_object()
          serializer = self.get_serializer(instance, data=request.data, partial=partial)
          serializer.is_valid(raise_exception=True)
          self.perform_update(serializer)

          return response.Response(
               {
                    "profile": serializer.data,
                    "message": "User profile updated successfully.",
                    # "data": serializer.data,
               },
               status=status.HTTP_200_OK,
          )