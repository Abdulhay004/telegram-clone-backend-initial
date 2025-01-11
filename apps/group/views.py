from rest_framework import generics,status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.response import Response
from .models import Group, GroupPermission
from .serializers import GroupSerializer, GroupPermissionsSerializer
from .paginations import CustomPagination
from .permissions import IsOwnerOrReadOnly, IsAuthenticated

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