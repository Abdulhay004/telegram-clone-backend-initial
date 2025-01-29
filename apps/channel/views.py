from rest_framework import generics,status,  serializers, viewsets
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Channel, ChannelMembership, User, ChannelMessage, ChannelScheduledMessage
from .serializers import (
    ChannelSerializer, MembershipSerializer,
    MessageSerializer, ScheduledMessageSerializer)

from django.db.models import Q
from django.shortcuts import get_object_or_404

from share.tasks import send_push_notification
from .tasks import send_channel_scheduled_message

from .permissions import IsOwnerOrReadOnly
from .paginations import CustomPagination

from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)

class ChannelListCreateView(generics.ListCreateAPIView):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(Q(owner=user) | Q(memberships__user=user)).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ChannelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'pk'

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(Q(owner=user) | Q(memberships__user=user)).distinct().order_by('-created_at')
        return queryset

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied('You do not have permission to delete this group.')
        instance.delete()

class MembershipListCreateView(generics.ListCreateAPIView):
        queryset = ChannelMembership.objects.all()
        serializer_class = MembershipSerializer
        permission_classes = [IsAuthenticated]
        pagination_class = CustomPagination

        def get_queryset(self):
            channel_id = self.kwargs['channel_id']
            return ChannelMembership.objects.filter(channel_id=channel_id)

        def perform_create(self, serializer):
               channel_id = self.kwargs['channel_id']
               channel = Channel.objects.filter(id=channel_id).first()
               if channel.owner != self.request.user:
                    raise PermissionDenied('You do not have permission to delete this group.')
               user_id = self.request.data.get("user_id")
               user = User.objects.get(id=user_id)
               serializer.save(channel=channel, user=user)

class MembershipDetailView(generics.RetrieveUpdateDestroyAPIView):
        queryset = ChannelMembership.objects.all()
        serializer_class = MembershipSerializer
        permission_classes = [IsAuthenticated]

        def perform_update(self, serializer):
            membership = self.get_object()
            channel = membership.channel
            if channel.owner != self.request.user:
                raise PermissionDenied('You do not have permission to delete this group.')
            serializer.save()

        def perform_destroy(self, instance):
            instance.delete()

class MessageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request, channel_id=None):
        channel = get_object_or_404(Channel, id=channel_id)
        messages = channel.messages.all()
        serializer = MessageSerializer(messages, many=True)
        return Response({"results": serializer.data})

    def create(self, request, channel_id=None):
        channel = get_object_or_404(Channel, id=channel_id)
        member = ChannelMembership.objects.filter(channel=channel).first()
        if channel.owner != request.user:
            raise PermissionDenied('You do not have permission to create messages in this channel.')
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(channel=channel, sender=request.user)
            send_push_notification.delay(str(member.user.id), f"New Message in {channel.name}", message.text)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def retrieve(self, request, channel_id=None, message_id=None):
        message = get_object_or_404(ChannelMessage, id=message_id, channel__id=channel_id)
        serializer = MessageSerializer(message)
        return Response(serializer.data)

    def partial_update(self, request, channel_id=None, message_id=None):
        message = get_object_or_404(ChannelMessage, id=message_id, channel__id=channel_id)
        if message.channel.owner != request.user:
            raise PermissionDenied('You do not have permission to update this message.')

        serializer = MessageSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, channel_id=None, message_id=None):
        message = get_object_or_404(ChannelMessage, id=message_id, channel__id=channel_id)
        if message.channel.owner != request.user:
            raise PermissionDenied('You do not have permission to delete this message.')

        message.delete()
        return Response(status=204)

class ScheduleMessageView(generics.CreateAPIView):
    queryset = ChannelScheduledMessage.objects.all()
    serializer_class = ScheduledMessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        channel = Channel.objects.get(owner=self.request.user)
        user = self.request.user
        if channel.owner != user:
            raise PermissionDenied("You do not have permission to schedule messages.")
        serializer.save(channel=channel, sender=user)
        send_channel_scheduled_message.delay()

class LikeRemoveMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, channel_id, message_id):
        try:
            message = ChannelMessage.objects.get(id=message_id, channel_id=channel_id)
        except ChannelMessage.DoesNotExist:
            return Response({"detail": "Message not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user in message.likes.all():
            return Response({"detail": "Message already liked."}, status=status.HTTP_400_BAD_REQUEST)
        message.likes.add(request.user)
        return Response({"detail": "Message liked."}, status=status.HTTP_200_OK)

    def delete(self, request, channel_id, message_id):
        try:
            message = ChannelMessage.objects.get(id=message_id, channel_id=channel_id)
        except ChannelMessage.DoesNotExist:
            return Response({"detail": "Message not found."}, status=status.HTTP_404_NOT_FOUND)
        if request.user not in message.likes.all():
            return Response({"detail": "Like not found."}, status=status.HTTP_404_NOT_FOUND)
        message.likes.remove(request.user)
        return Response({"detail": "Like removed."}, status=status.HTTP_200_OK)

