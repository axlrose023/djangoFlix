from django.db import models
from .manager import CustomUserManager
from django.contrib.auth.models import AbstractUser


# Create your models here.

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(default='djangoflix/static/images/profile.jpg', upload_to='media')

    def __str__(self):
        return self.user.email
