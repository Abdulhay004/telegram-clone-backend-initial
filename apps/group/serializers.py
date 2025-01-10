from rest_framework import serializers
from .models import Group, GroupPermission, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone_number", "user_name", "bio", "birth_date", "first_name", "last_name"]

class GroupSerializer(serializers.ModelSerializer):
    owner = UserSerializer(required=False)
    members = UserSerializer(many=True, required=False)
    class Meta:
        model = Group
        fields = ['id', 'name', 'owner', 'members', 'is_private', 'created_at', 'updated_at']


class GroupPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupPermission
        fields = ['__all__']