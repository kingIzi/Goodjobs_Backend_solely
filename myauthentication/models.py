from django.db import models
from django.contrib.auth.models import AbstractUser, User
from goodjobs.settings import AUTH_USER_MODEL
from django.conf import settings


class OTP(models.Model):
    is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=1000)
    first_name = models.CharField(max_length=1000, blank=True)
    last_name = models.CharField(max_length=1000,blank=True)
    email = models.CharField(max_length=1000,blank=True)
    otp_value = models.CharField(max_length=100)
    request_count = models.IntegerField(default=0,blank=True,null=True)  # Track number of OTP requests
    last_requested = models.DateField(auto_now_add=True, blank=True, null=True)  # Track the date of the last OTP request

    def __str__(self):
        return self.phone_number


class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    user_image = models.FileField(blank=True,null=True)
