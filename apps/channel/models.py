from django.db import models
import uuid

from .enums import ChannelType, ChannelMembershipType

from user.models import User


class Channel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    owner = models.ForeignKey(User,on_delete=models.CASCADE)
    channel_type = models.CharField(max_length=30,choices=ChannelType.choices(),default=ChannelType.PUBLIC.value)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'channel'
        verbose_name='Channel'
        verbose_name_plural='Channels'
        ordering = ['-created_at']
        unique_together = ('name', 'owner')

    def __str__(self):
        return self.name

class ChannelMembership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=6, choices=ChannelMembershipType.choices(), default=ChannelMembershipType.MEMBER.value)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.channel.name}"

    class Meta:
        db_table = 'channelMembership'
        verbose_name='ChannelMembership'
        verbose_name_plural='ChannelMemberships'
        ordering = ['-created_at']
        unique_together = ('channel', 'user')

class ChannelMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_channel_messages', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def media(self):
        return self.image or self.file

    def __str__(self):
        return f"Message from {self.sender.username} in {self.channel.name}"

class ChannelScheduledMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    scheduled_time =  models.DateTimeField()
    sent = models.BooleanField(default=False)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


