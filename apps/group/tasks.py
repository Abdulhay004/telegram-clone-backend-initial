from asgiref.sync import async_to_sync
from celery import shared_task
from celery.utils.log import get_task_logger
from channels.layers import get_channel_layer
from django.utils import timezone

from group.models import GroupScheduledMessage, GroupMessage
from group.serializers import GroupMessageSerializer

logger = get_task_logger(__name__)

@shared_task
def send_group_scheduled_message():
    logger.info("Running Scheduled group message.")
    try:
        now = timezone.now()
        scheduled_messages = GroupScheduledMessage.objects.filter(
            scheduled_time__lte=now,sent=False
        )
        if not scheduled_messages.exists():
            logger.info("No scheduled message to send.")
            return
        for scheduled_message in scheduled_messages:
            group_message=GroupMessage.objects.create(
                group=scheduled_message.group,
                sender=scheduled_message.sender,
                text=scheduled_message.text
            )
            scheduled_message.sent = True
            scheduled_message.save()
            logger.info(f"Group scheduled message sent {group_message.text}")
            serializer = GroupMessageSerializer(group_message)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"group__{scheduled_message.group.id}",
                {"type":"group_message","text":serializer.data}
            )
            logger.info(f"Message sent: {group_message.text}")
    except Exception as e:
        logger.error(f"Error send scheduled message task: {str(e)}")
