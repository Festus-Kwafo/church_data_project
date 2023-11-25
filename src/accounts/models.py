# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django_countries.fields import CountryField
from accounts.managers import AccountManager


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    phonenumber = models.CharField(max_length=10, null=True, blank=True)
    branch_name = models.CharField(max_length=100, default="accra")
    email = models.EmailField()
    otp_number = models.IntegerField(default=000000)
    otp_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)
    planted_on = models.DateField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    country = CountryField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Django stuff for authentication
    USERNAME_FIELD = "username"
    objects = AccountManager()
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    user_must_change_password = models.BooleanField(..., default=True)

    class Meta:
        db_table = "branches"

    def count_notifications(self):
        return self.notifications.filter(read=False).count()

    def get_notifications(self):
        notifications = self.notifications.filter().order_by("-id")
        notifications.update(read=True)
        return notifications[:100]

    def __str__(self):
        return self.branch_name

