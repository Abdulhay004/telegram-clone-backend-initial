from django.db import models
from django.utils import timezone
import uuid

from .enums import ChannelType, ChannelMembershipType

from user.models import User
from share.models import (
    BaseModel, BaseMessageModel,
    BaseScheduledMessageModel, BaseStartModel)

class Channel(BaseModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    type = models.CharField(max_length=30,choices=ChannelType.choices(),default=ChannelType.PUBLIC.value)

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

class ChannelMembership(BaseStartModel):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=6, choices=ChannelMembershipType.choices(), default=ChannelMembershipType.MEMBER.value)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.channel.name}"

    class Meta:
        db_table = 'channelMembership'
        verbose_name='ChannelMembership'
        verbose_name_plural='ChannelMemberships'
        ordering = ['-created_at']
        unique_together = ('channel', 'user')

class ChannelMessage(BaseMessageModel):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_channel_messages', blank=True)

    @property
    def media(self):
        return self.image or self.file

    def __str__(self):
        return f"Message from {self.sender.username} in {self.channel.name}"

class ChannelScheduledMessage(BaseScheduledMessageModel):
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)

    def __str__(self):
        return f"Scheduled message from {self.sender.username} in {self.channel.name} at {self.scheduled_time}"


