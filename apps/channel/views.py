from rest_framework import generics,status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Channel
from .serializers import (
    ChannelSerializer)

from django.db.models import Q

from .permissions import IsOwnerOrReadOnly
from .paginations import CustomPagination

from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)

# class ChannelListCreateView(generics.ListCreateAPIView):
#     queryset = Channel.objects.all()
#     serializer_class = ChannelSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = CustomPagination
#
#     def get_queryset(self):
#         user = self.request.user
#         return self.queryset.filter(Q(owner=user) | Q(memberships__user=user)).distinct().order_by('-created_at')
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)
#
# class ChannelDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Channel.objects.all()
#     serializer_class = ChannelSerializer
#     permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
#     lookup_field = 'pk'
#
#     def get_queryset(self):
#         user = self.request.user
#         queryset = self.queryset.filter(Q(owner=user) | Q(memberships__user=user)).distinct().order_by('-created_at')
#         return queryset
#
#     def perform_destroy(self, instance):
#         if instance.owner != self.request.user:
#             raise PermissionDenied('You do not have permission to delete this group.')
#         instance.delete()

class ChannelListCreateView(generics.ListCreateAPIView):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class ChannelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
