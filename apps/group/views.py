from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from .models import Group, GroupPermission
from .serializers import GroupSerializer
from .paginations import CustomPagination

class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        group = serializer.save(owner=self.request.user)
        GroupPermission.objects.create(group=group, can_send_messages=True, can_send_media=True)

class GroupDetailView(generics.RetrieveDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def perform_destroy(self, instance):
        if instance.owner != self.request.user:
            raise PermissionDenied('You do not have permission to delete this group.')
        instance.delete()