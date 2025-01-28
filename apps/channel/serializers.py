from rest_framework import serializers
from .models import Channel, ChannelMembership
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
