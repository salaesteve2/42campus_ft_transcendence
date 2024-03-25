# models.py

from django.contrib.auth.models import User
from django.db import models

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    two_factor_auth_enabled = models.BooleanField(default=False)