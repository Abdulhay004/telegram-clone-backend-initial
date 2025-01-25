from django.db import models
import uuid

from user.models import User
from share.models import (
    BaseModel, BaseMessageModel, BaseScheduledMessageModel)

class Group(BaseModel):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    members = models.ManyToManyField(User, related_name='group_members')
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class GroupParticipant(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

class GroupMessage(BaseMessageModel):
    group = models.ForeignKey(Group, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.SET('delete_user'), related_name='send_messages')
    image = models.ImageField(upload_to='group_messages/', blank=True, null=True)
    file = models.FileField(upload_to='group_files/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    liked_by = models.ManyToManyField(User, related_name='liked_group_messages', blank=True)

    class Meta:
        ordering = ['-created_at']

class GroupScheduledMessage(BaseScheduledMessageModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Scheduled message from {self.sender.username} for {self.group.name}"

class GroupPermission(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    can_send_messages = models.BooleanField(default=True)
    can_send_media = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Permissions for {self.group.name}"

