from django.db import models
from django.utils import timezone


class EmailOTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
    verified = models.BooleanField(default=False)
    attempt = models.PositiveIntegerField(default=0)
    resend_count = models.PositiveIntegerField(default=0)
    last_resend = models.DateTimeField(auto_now=True)

    def is_expired(self):
        return timezone.now() > self.expired_at
    
    def __str__(self):
        return self.email
    
class PendingUser(models.Model):
    username=models.CharField(max_length=150)
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=128)
    created_at=models.DateTimeField(auto_now_add=True)