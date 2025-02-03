from celery import shared_task
from .models import ChannelScheduledMessage, ChannelMessage
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from celery.utils.log import get_task_logger
from share.tasks import send_push_notification
from .serializers import ScheduledMessageSerializer

logger = get_task_logger(__name__)

@shared_task
def send_channel_scheduled_message():
    logger.info("Running scheduled message task.")
    try:
        now = timezone.now()
        scheduled_messages = ChannelScheduledMessage.objects.filter(
            scheduled_time__lte=now, sent=False
        )
        if not scheduled_messages.exists():
            logger.info("No scheduled messages to send.")
            return

        logger.info(f"Found {scheduled_messages.count()} scheduled messages to send.")
        for scheduled_message in scheduled_messages:
            message = ChannelMessage.objects.create(
                channel=scheduled_message.channel,
                sender=scheduled_message.sender,
                text=scheduled_message.text,
            )
            scheduled_message.sent = True
            scheduled_message.save()

            for membership in scheduled_message.channel.memberships.all():
                notification_preference = getattr(membership.user, "notifications", None)
                if notification_preference and notification_preference.notifications_enabled:
                    send_push_notification.delay(notification_preference.device_token,
                                                 f"New Message in {scheduled_message.channel.name}",
                                                 scheduled_message.text)

            logger.info(f"Message sent: {message.text}")
    except Exception as e:
        logger.error(f"Error in send_scheduled_message task: {str(e)}")
