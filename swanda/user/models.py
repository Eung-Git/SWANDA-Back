from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from datetime import timedelta

MAJOR_CHOICES = [
    (0, 'software'),
    (1, 'ai'),
    (2, 'others'),
]

class User(AbstractUser):
    username = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=128)
    nickname = models.CharField(max_length=10, unique=True)
    major = models.IntegerField(choices=MAJOR_CHOICES, blank=True, null=True)
    email = models.CharField(max_length=255, unique=True)
    verification_code = models.CharField(max_length=15, blank=True, null=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nickname']
    
class TemporaryUser(models.Model):
    email = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=6)
    is_certified = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def is_expired(self):
        return now() > self.updated_at + timedelta(minutes=10)