from rest_framework import serializers
from .models import Group, GroupPermission, User, GroupMessage

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

class GroupPermissionsSerializer(serializers.Serializer):
    can_send_messages = serializers.BooleanField(required=True)
    can_send_media = serializers.BooleanField(required=True)

    def validate_can_send_messages(self, value):
        if not isinstance(value, bool):
            raise serializers.ValidationError("Value must be a boolean.")
        return value

    def validate_can_send_media(self, value):
        if not isinstance(value, bool):
            raise serializers.ValidationError("Value must be a boolean.")
        return value

class GroupMembersSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())

    class Meta:
        model = Group
        fields = ['members']

class GroupMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMessage
        firlds = '__all__'