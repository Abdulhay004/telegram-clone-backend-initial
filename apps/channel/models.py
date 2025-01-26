from django.db import models
from django.utils import timezone
import uuid

from .enums import ChannelType, ChannelMembershipType

from user.models import User
from share.models import (
    BaseModel, BaseMessageModel,
    BaseScheduledMessageModel, BaseStartModel)

class Channel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # 'auth.User' - Django foydalanuvchi modeli
    type = models.CharField(max_length=30,choices=ChannelType.choices(),default=ChannelType.PUBLIC.value)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def channel_type(self):
        return ChannelType(self.type).value

    class Meta:
        db_table = 'channel'
        verbose_name='Channel'
        verbose_name_plural='Channels'
        ordering = ['-created_at']
        unique_together = ('name', 'owner')

    def __str__(self):
        return self.name

class ChannelMembership(models.Model):
    # channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=6, choices=ChannelMembershipType.choices(), default=ChannelMembershipType.MEMBER.value)
    # joined_at = models.DateTimeField(auto_now_add=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 'auth.User' - Django foydalanuvchi modeli
    # role = models.CharField(max_length=6, choices=ROLE_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = 'channelMembership'
        verbose_name='ChannelMembership'
        verbose_name_plural='ChannelMemberships'
        ordering = ['-created_at']
        unique_together = ('channel', 'user')

class ChannelMessage(models.Model):
    # channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    # sender = models.ForeignKey(User, on_delete=models.CASCADE)
    # image = models.ImageField(upload_to='images/', blank=True, null=True)
    # file = models.FileField(upload_to='files/', blank=True, null=True)
    # likes = models.ManyToManyField(User, related_name='liked_channel_messages', blank=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)  # 'auth.User' - Django foydalanuvchi modeli
    text = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_channel_messages', blank=True)  # Foydalanuvchilar uchun layk
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def media(self):
        return self.image or self.file

class ChannelScheduledMessage(models.Model):
    # channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    # sender = models.ForeignKey(User, on_delete=models.CASCADE)
    # image = models.ImageField(upload_to='images/', blank=True, null=True)
    # file = models.FileField(upload_to='files/', blank=True, null=True)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)  # 'auth.User' - Django foydalanuvchi modeli
    text = models.TextField()
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    scheduled_time = models.DateTimeField()
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

