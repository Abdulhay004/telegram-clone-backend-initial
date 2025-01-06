from django.contrib.postgres.indexes import HashIndex
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractUser, Permission

import uuid

from .managers import UserManager

class User(AbstractUser):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    phone_number = models.CharField(max_length=18,unique=True)
    bio = models.CharField(max_length=200,null=True,blank=True)
    user_name =  models.CharField(max_length=200, blank=True, null=True)
    username =  models.CharField(max_length=200, blank=True, null=True)
    birth_date = models.DateField(null=True,blank=True)
    is_verified = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True,blank=True)
    last_login = models.DateTimeField(null=True,blank=True)
    is_2fa_enabled = models.BooleanField(default=False)
    otp_secret = models.CharField(max_length=200,null=True,blank=True)
    email = models.EmailField(null=True,blank=True)
    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []
    objects = UserManager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user_name or self.phone_number

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
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

class UserAvatar(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.user_name}'s avatar"


class DeviceInfo(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.device_name} - {self.ip_address}"

class Contact(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    friend = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40, blank=True, null=True)
    phone_number = models.CharField(max_length=18,blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contact'
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ['-created_at']

class NotificationPreference(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notifications_enabled = models.BooleanField(default=False)
    device_token = models.CharField(max_length=255, null=True, blank=True)

