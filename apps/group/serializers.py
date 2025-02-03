from rest_framework import serializers
from .models import Group, GroupPermission, GroupMessage, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "phone_number", "user_name", "bio", 'is_online', "birth_date"]

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
    group = GroupSerializer(read_only=True)
    sender = UserSerializer(read_only=True)
    liked_by = UserSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    class Meta:
        model = GroupMessage
        fields = ['id','group','sender','text','image','file', 'sent_at','is_read','liked_by','likes_count']
        read_only_fields = ['liked_by']

    def get_likes_count(self,obj):
        return obj.liked_by.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = str(representation['id'])
        return representation