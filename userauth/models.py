from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# ---------------- USER MANAGER ---------------- #


class UserManager(BaseUserManager):

    def create_user(self, email, name, role, phone, password=None, **extra_fields):

        if not email:
            raise ValueError("Users must have an email address")

        if not name:
            raise ValueError("Users must have a name")

        if not role:
            raise ValueError("Users must have a role")

        email = self.normalize_email(email)

        user = self.model(
            email=email, name=name, role=role, phone=phone, **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, phone, password=None, **extra_fields):

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(
            email, name, self.model.USER, phone, password, **extra_fields
        )


# ---------------- USER MODEL ---------------- #


class User(AbstractBaseUser, PermissionsMixin):

    USER = 1
    PROVIDER = 2

    ROLE_CHOICES = (
        (USER, "User"),
        (PROVIDER, "Provider"),
    )

    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(max_length=20, unique=True)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=USER)

    # Password reset fields
    password_reset_otp = models.CharField(max_length=6, blank=True, null=True)
    password_reset_otp_created_at = models.DateTimeField(blank=True, null=True)
    password_reset_token = models.CharField(max_length=40, blank=True, null=True)

    date_joined = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phone"]

    objects = UserManager()

    def __str__(self):
        return self.email


# ---------------- PROFILE MODEL ---------------- #


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    location = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.FileField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.email


# Auto create profile
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()
