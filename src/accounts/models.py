# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from accounts.managers import AccountManager



class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    phonenumber = models.CharField(max_length=10, null=True, blank=True)
    branch = models.CharField(max_length=100, default="accra")
    email = models.EmailField()
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Django stuff for authentication
    USERNAME_FIELD = "username"
    objects = AccountManager()
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "users"

    def count_notifications(self):
        return self.notifications.filter(read=False).count()

    def get_notifications(self):
        notifications = self.notifications.filter().order_by("-id")
        notifications.update(read=True)
        return notifications[:100]

    def __str__(self):
        return self.branch
