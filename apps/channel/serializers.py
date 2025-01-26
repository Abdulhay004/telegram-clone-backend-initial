from rest_framework import serializers
from .models import Channel, User

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