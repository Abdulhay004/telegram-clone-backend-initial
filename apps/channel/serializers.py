from rest_framework import serializers
from .models import Channel, ChannelMembership, ChannelMessage
from user.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone_number", "user_name", "bio", "birth_date", "first_name", "last_name"]

class ChannelSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    class Meta:
        model = Channel
        fields = ['id', 'name', 'description', 'channel_type', 'owner', 'created_at', 'updated_at']
        read_only_fields = ['owner', 'description']

class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ChannelMembership
        fields = ['id', 'user', 'role', 'joined_at']
        read_only_field = ['user']

class MessageSerializer(serializers.ModelSerializer):
    channel = ChannelSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    liked_by = UserSerializer(many=True, read_only=True)
    class Meta:
        model = ChannelMessage
        fields = ['id', 'channel', 'user', 'text', 'media', 'file', 'liked_by', 'created_at']
        read_only_fields = ['id', 'channel', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['file'] = instance.file.url if instance.file else None
        representation['image'] = instance.image.url if instance.image else None
        representation['media'] = representation['image'] or representation['file']
        return representation