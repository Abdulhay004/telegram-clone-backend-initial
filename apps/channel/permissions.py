from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from .models import Channel, ChannelMembership, ChannelMembershipType

class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.owner == request.user
