from rest_framework.permissions import BasePermission, IsAuthenticated
from .models import GroupPermission

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.owner == request.user

class IsGroupSendMedia(BasePermission):
    def has_object_permission(self, request, view, obj):
        permis = GroupPermission.objects.filter(group=obj).first()
        return permis.can_send_media == True