from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
import uuid
import pytz

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class BaseStartModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class BaseMessageModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class BaseScheduledMessageModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    scheduled_time =  models.DateTimeField(default=datetime.now() + timedelta(days=1))
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    # def save(self, *args, **kwargs):
    #     # scheduled_time ni UTC ga aylantirish
    #     # if not isinstance(self.scheduled_time, str):
    #     if self.scheduled_time and self.scheduled_time.tzinfo is None:
    #             self.scheduled_time = datetime(2025, 1, 26, 23, 1, 11, 553317)
    #     super().save(*args, **kwargs)


