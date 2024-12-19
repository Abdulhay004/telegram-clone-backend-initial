from django.contrib.postgres.indexes import HashIndex
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser, Permission

from .managers import UserManager

class User(AbstractUser):
    phone_number = models.CharField(max_length=20, unique=True, blank=True)
    user_name = models.CharField(max_length=100, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    bio = models.CharField(max_length=400, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=255, blank=True, null=True)

    objects = UserManager()
    USERNAME_FIELD = "phone_number"

    def __str__(self):
        return self.user_name

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=~Q(phone_number=None),
                name="check_phone_number",
            )
        ]
        indexes = [
            HashIndex(fields=['first_name'], name='%(class)s_first_name_hash_idx'),
            HashIndex(fields=['last_name'], name='%(class)s_last_name_hash_idx'),
            models.Index(fields=['phone_number'], name='%(class)s_phone_number_idx'),
        ]
        permissions = [
            ("can_send_message", "Can send messages"),
            ("can_create_group", "Can create groups"),
            ("can_add_contact", "Can add contacts"),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_superuser:
            all_permissions = Permission.objects.all()
            self.user_permissions.set(all_permissions)