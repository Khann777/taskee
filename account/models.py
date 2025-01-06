from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Email Address")
    username = models.CharField(max_length=30, unique=True, verbose_name="Username")
    password = models.CharField(max_length=255)
    avatar = models.ImageField(upload_to="avatar", null=True, blank=True, verbose_name="Avatar Image")
    bio = models.TextField(null=True, blank=True, verbose_name="Bio")
    telegram_chat_id = models.CharField(max_length=20, verbose_name="Telegram Chat ID", blank=True, null=True)
    is_premium = models.BooleanField(default=False, verbose_name="Is premium?")
    premium_expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Premium Expiration Date")


    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f'{self.username} - {self.email}'
