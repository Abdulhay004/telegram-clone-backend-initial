        
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
# from djangochannelsrestframework.observer import ObserverModelInstanceMixin
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import ObserverModelInstanceMixin
from django.contrib.auth.models import AnonymousUser
from djangochannelsrestframework.observer.generics import action

from user.models import User
from .models import Chat, ChatParticipant, Message
from .serializers import ChatSerializer, MessageSerializer, UserSerializer

# ChatConsumer WebSocket orqali muloqot qilish va foydalanuvchilar o'rtasidagi suhbatni boshqarish uchun ishlatiladi
class ChatConsumer(ObserverModelInstanceMixin, GenericAsyncAPIConsumer, AsyncJsonWebsocketConsumer):
    queryset = Chat.objects.all() # Chat obyektlarining umumiy ro'yxati
    serializer_class = ChatSerializer # Chat obyektlarini serialyash uchun serializer
    lookup_field = 'pk' # Qidiruv uchun asosiy kalit maydon

    # WebSocket ulanishini o'rnatish uchun ishlatiladi
    async def connect(self):
        self.user = self.scope.get('user', AnonymousUser()) # Foydalanuvchini olish
        self.chat_id = self.scope['url_route']['kwargs']['pk'] # Chat ID sini olish
        self.chat = await self.get_chat(self.chat_id) # Chat obyektini olish
        self.participants = await self.current_users(self.chat) # Hozirgi ishtirokchilarni olish

        # Agar foydalanuvchi autentifikatsiyadan o'tmagan bo'lsa, ulanishni yopamiz
        if not self.user.is_authenticated:
            return await self.close()

        # Agar chat mavjud bo'lmasa, ulanishni yopamiz
        if not self.chat:
            return await self.close()

        # Agar foydalanuvchi chat ishtirokchisi bo'lmasa, ulanishni yopamiz
        if self.user.id not in {self.chat.owner_id, self.chat.user_id}:
            return await self.close()

        # WebSocket guruhiga foydalanuvchini qo'shish
        await self.channel_layer.group_add(f"chat__{self.chat_id}", self.channel_name)
        await self.add_user_to_chat(self.chat_id) # Foydalanuvchini chatga qo'shish
        await self.accept() # Ulanishni qabul qilish
        await self.update_user_status(is_online=True) # Foydalanuvchi holatini yangilash
        await self.notify_users() # Barcha foydalanuvchilarga yangi ishtirokchilar haqida xabar berish
        await self.get_messages(self.chat_id) # Oldingi xabarlarni olish

    # WebSocket uzilganda bajariladi
    async def disconnect(self, code):
        if self.user.is_authenticated:
            await self.remove_user_from_chat(self.chat_id) # Foydalanuvchini chatdan olib tashlash
            await self.update_user_status(is_online=False) # Foydalanuvchi holatini yangilash
            await self.notify_users() # Foydalanuvchilarga yangilangan holatni yuborish
            await self.channel_layer.group_discard(
                f"chat__{self.chat_id}", self.channel_name
            )

        await super().disconnect(code)

    # Barcha foydalanuvchilarga ishtirokchilar ro'yxatini yuborish
    async def notify_users(self):
        participants = await self.current_users(self.chat) # Hozirgi ishtirokchilarni olish
        users = await self.serialize_users(participants) # Ishtirokchilarni seriallash
        await self.channel_layer.group_send(
            f"chat__{self.chat_id}", {"type": "update_users", "users": users}
        )

# Foydalanuvchilarni yangilash xabarini yuborish
    async def update_users(self, event):
        await self.send_json({'users': event['users']})  # JSON formatida yuborish
    # Xabarlarni olish uchun endpoint
    @action()
    async def get_messages(self, pk, **kwargs):
        messages = await self.fetch_messages(pk)  # Xabarlarni bazadan olish
        serialized_messages = await self.serialize_messages(messages)  # Xabarlarni seriyalash
        await self.send_json({
            'action': 'get_messages', 'messages': serialized_messages
        })
    # Chatdan barcha xabarlarni olish uchun yordamchi metod
    @database_sync_to_async
    def fetch_messages(self, pk: int):
        try:
            chat = Chat.objects.get(pk=pk)  # Chat obyektini olish
            return list(chat.messages.order_by('sent_at'))  # Xabarlarni sanaga ko'ra tartiblash
        except Chat.DoesNotExist:
            return []  # Agar chat mavjud bo'lmasa, bo'sh ro'yxatni qaytarish
    # Xabarlarni seriyalash
    @database_sync_to_async
    def serialize_messages(self, messages):
        return MessageSerializer(messages, many=True, context={'user': self.user}).data
    # Bitta xabarni seriyalash
    @database_sync_to_async
    def serialize_message(self, message):
        return MessageSerializer(message).data
    # Chat obyektini olish
    @database_sync_to_async
    def get_chat(self, pk: int):
        try:
            return Chat.objects.get(pk=pk)  # Chat obyektini qaytarish
        except Chat.DoesNotExist:
            return None  # Agar chat topilmasa, None qaytarish
    # Chatdagi hozirgi ishtirokchilarni olish
    @database_sync_to_async
    def current_users(self, chat: Chat):
        participants = ChatParticipant.objects.filter(chat=chat).select_related("user")
        return [UserSerializer(participant.user).data for participant in participants]

    # Foydalanuvchini chatdan olib tashlash
    @database_sync_to_async
    def remove_user_from_chat(self, chat_id: int):
        ChatParticipant.objects.filter(user=self.user, chat_id=chat_id).delete()

    # Foydalanuvchini chatga qo'shish
    @database_sync_to_async
    def add_user_to_chat(self, chat_id: int):
        chat = Chat.objects.get(pk=chat_id)
        if not ChatParticipant.objects.filter(user=self.user, chat=chat).exists():
            ChatParticipant.objects.create(user=self.user, chat=chat)

    # Foydalanuvchilarni seriallash
    @database_sync_to_async
    def serialize_users(self, users):
        return UserSerializer(users, many=True).data

    # Foydalanuvchi holatini yangilash
    @database_sync_to_async
    def update_user_status(self, is_online):
        self.user.is_online = is_online  # Foydalanuvchini onlayn yoki oflayn qilish
        self.user.update_last_seen()  # Oxirgi ko'rilgan vaqtni yangilash
        self.user.save()  # O'zgarishlarni saqlash

    async def chat_message(self, event):
        """
        Chatdagi xabarni yuboradi.
        event["text"] orqali xabar matnini yuboradi.
        """
        await self.send_json({"action": "new_message", "data": event["text"]})

    @action()
    async def create_message(self, pk, data, **kwargs):
        # pk = str(pk)
        """
        Yangi xabar yaratish va uni chat guruhiga yuborish.
        pk - chatning identifikatori, data - xabar matni.
        """
        chat = await self.get_chat(pk)
        if not chat:
            return

        user = self.scope["user"]
        recipient = await self.get_recipient(chat, user)
        if not recipient:
            return

        message = await self.save_message(chat, user, data)
        serialized_message = await self.serialize_message(message)

        await self.channel_layer.group_send(
            f"chat__{pk}", {"type": "chat_message", "text": serialized_message}
        )

    @database_sync_to_async
    def save_message(self, chat: Chat, user: User, data: dict):
        """
        Yangi xabarni saqlash.
        Xabar matni, rasm yoki fayl saqlanadi.
        """
        valid_keys = {"text", "image", "file"}
        message_data = {key: data.get(key) for key in valid_keys if data.get(key)}

        message = Message.objects.create(chat=chat, sender=user, **message_data)
        return message

    @database_sync_to_async
    def get_recipient(self, chat: Chat, user: User):
        """
        Xabarni qabul qiluvchisini olish.
        Agar foydalanuvchi chat egasi bo'lsa, unda ishtirokchi (user) oladi.
        """
        if chat.owner == user:
            return chat.user
        elif chat.user == user:
            return chat.owner
        return None

