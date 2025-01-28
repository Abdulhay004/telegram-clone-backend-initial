from rest_framework import generics,status,  serializers
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Channel, ChannelMembership, User
from .serializers import (
    ChannelSerializer, MembershipSerializer)

from django.db.models import Q

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

