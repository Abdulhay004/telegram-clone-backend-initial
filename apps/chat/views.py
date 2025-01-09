from django.shortcuts import render
from rest_framework import generics, pagination, viewsets, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.permissions import IsAuthenticated
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Chat, Message
from .paginations import CustomPagination
from .serializers import ChatSerializer, MessageSerializer

class ChatAPIView(generics.ListCreateAPIView):
    queryset = Chat.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(owner=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save()

class ChatDetailAPIView(generics.ListAPIView, generics.DestroyAPIView):
    queryset = Chat.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ChatSerializer
    lookup_field = 'id'

    def get(self, request, *args, **kwargs):
        try:
            chat = Chat.objects.get(owner=request.user)
            serializer = self.get_serializer(chat)
            return Response(serializer.data)
        except Chat.DoesNotExist:
            return Response({"detail": "Chat not found."}, status=status.HTTP_404_NOT_FOUND)

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise NotFound("Chat not found.")
        else:
            instance.delete()

class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return Message.objects.filter(chat_id=chat_id)

    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        message = serializer.save(sender=self.request.user, chat_id=chat_id)

        if message.file or message.image:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"chat_{message.chat.id}",
                {
                    "type": "chat_message",
                    "message_id": str(message.id),
                    "sender": {
                        "id": str(message.sender.id),
                        "user_name": str(message.sender.username),
                    },
                    "text": message.text,
                    "image": message.image.url if message.image.url else None,
                    "file": message.file if message.file else None,
                    "sent_at": message.sent_at.isoformat(),
                },
            )
