from rest_framework import generics,status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Group, GroupPermission, GroupMessage
from .serializers import (
    GroupSerializer, GroupPermissionsSerializer,
    GroupMembersSerializer, GroupMessageSerializer)
from .paginations import CustomPagination
from .permissions import IsOwnerOrReadOnly, IsAuthenticated, IsGroupSendMedia

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.db import transaction

import logging

logger = logging.getLogger(__name__)

class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        group = serializer.save(owner=self.request.user)
        GroupPermission.objects.create(group=group, can_send_messages=True, can_send_media=True)

class GroupDetailView(generics.RetrieveDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'pk'

    def get_queryset(self):
        queryset = self.queryset.filter(owner=self.request.user)
        if not queryset.exists() and not self.request.method == 'GET':
            raise PermissionDenied('You do not have permission to access this group.')
        return queryset

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied('You do not have permission to delete this group.')
        instance.delete()

class GroupPermissionsUpdateView(generics.UpdateAPIView):
    serializer_class = GroupPermissionsSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Group.objects.filter(owner=self.request.user)

    def patch(self, request, *args, **kwargs):
        group = self.get_object()
        if group.owner != request.user:
            raise PermissionDenied("You do not have permission to update permissions for this group.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_permission, created = GroupPermission.objects.get_or_create(group=group)
        group_permission.can_send_messages = serializer.validated_data.get('can_send_messages', group_permission.can_send_messages)
        group_permission.can_send_media = serializer.validated_data.get('can_send_media', group_permission.can_send_media)
        group_permission.save()

        return Response({"message": "Permissions updated successfully."})

class GroupMembershipsView(generics.GenericAPIView):
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'group_id'

    def get_object(self):
        group_id = self.kwargs[self.lookup_url_kwarg]
        return Group.objects.get(id=group_id)

    def get(self, request, *args, **kwargs):
        group = self.get_object()
        serializer = self.get_serializer(group)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        group = self.get_object()

        if group.is_private:
            return Response({"detail": "This group is private."}, status=status.HTTP_403_FORBIDDEN)
        if request.user in group.members.all():
            return Response({"detail": "You are already a member of this group."}, status=status.HTTP_400_BAD_REQUEST)

        group.members.add(request.user)
        return Response({"detail": "You have successfully joined the group."}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        group = self.get_object()

        if request.user in group.members.all():
            group.members.remove(request.user)
            return Response({"detail": "You have successfully left the group."}, status=status.HTTP_200_OK)

        return Response({"detail": "You are not a member of this group."}, status=status.HTTP_400_BAD_REQUEST)

class GroupMembersView(APIView):
    def patch(self, request, id, *args, **kwargs):
        try:
            group = Group.objects.get(id=id)
        except Group.DoesNotExist:
            return Response({"detail": "Group not found."}, status=status.HTTP_404_NOT_FOUND)

        if not group.is_private:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if group.is_private and not (request.user == group.owner or request.user in group.members.all()):
            return Response({"detail": "You do not have permission to add members to this group."}, status=status.HTTP_403_FORBIDDEN)

        serializer = GroupMembersSerializer(group, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GroupMessageView(generics.ListCreateAPIView):
   queryset = Group.objects.all()
   serializer_class = GroupMessageSerializer
   permission_classes = [IsAuthenticated, IsGroupSendMedia]
   pagination_class = CustomPagination
   lookup_url_kwarg = 'pk'

   def list(self, request, *args, **kwargs):
       group = self.get_object()
       if not group:
           return Response(data={"detail":"Group Not Found"},status=status.HTTP_404_NOT_FOUND)
       serializer = self.get_serializer(group.messages.all(),many=True)
       return Response(serializer.data)

   def perform_create(self, serializer):
       group=self.get_object()
       sender = self.request.user
       serializer.save(group=group,sender=sender)
