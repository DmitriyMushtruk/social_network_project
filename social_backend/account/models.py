import uuid

from django.contrib.auth.models import AbstractUser, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    class Roles(models.TextChoices):
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    image_s3_path = models.CharField(max_length=200, null=True, blank=True)
    role = models.CharField(max_length=9, choices=Roles.choices)

    title = models.CharField(max_length=80)
    is_blocked = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)
