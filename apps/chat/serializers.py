from rest_framework import serializers, exceptions, status
from rest_framework.exceptions import ValidationError
from .models import Chat, User, Message

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone_number", "user_name", "bio", "birth_date", "first_name", "last_name"]

class ChatSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    owner_id = serializers.UUIDField(write_only=True)
    user_id = serializers.UUIDField(write_only=True)
    participants = serializers.JSONField(default=list, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'owner', 'user', 'created_at', 'participants', 'owner_id', 'user_id']
        read_only_fields = ['id', 'owner', 'created_at', 'participants']

    def create(self, validated_data):
        owner_id = validated_data.pop('owner_id')
        user_id = validated_data.pop('user_id')

        owner = User.objects.get(id=owner_id)
        user = User.objects.get(id=user_id)

        if Chat.objects.filter(owner=owner, user=user).exists():
            raise ValidationError("Chat already exists between these users.", code=status.HTTP_400_BAD_REQUEST)

        chat = Chat.objects.create(owner=owner, user=user, **validated_data)
        return chat

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()  # Yoki boshqa kerakli serializatsiya
    liked_by = UserSerializer(many=True, read_only=True)  # Liked users
    chat = ChatSerializer(required=False)
    likes_count = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'text', 'image', 'file', 'sent_at', 'is_read', 'liked_by', 'likes_count']

    def get_likes_count(self, obj):
        return obj.liked_by.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = str(representation['id'])
        return representation

    def create(self, validated_data):
        liked_by_data = validated_data.pop('liked_by', None)

        message = Message.objects.create(**validated_data)

        if liked_by_data:
            for user in liked_by_data:
                message.liked_by.add(user)

        return message