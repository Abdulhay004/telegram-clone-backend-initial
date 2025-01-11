from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import action
from django.contrib.auth.models import AnonymousUser

from .models import Group, GroupParticipant
from .serializers import GroupMessageSerializer, UserSerializer

# GroupConsumer WebSocket ulanishini ishlatadigan Consumer bo'lib, guruhdagi foydalanuvchilarni boshqaradi.
class GroupConsumer(GenericAsyncAPIConsumer, AsyncJsonWebsocketConsumer):
    # Guruh uchun query set va serializer sinfi
    queryset = Group.objects.all()
    serializer_class = GroupMessageSerializer # faqat messagelar uchun kerak bo'lgani uchun message serializer ishlatiladi
    lookup_field = 'pk'

    async def connect(self):
        """WebSocket ulanishini boshlash."""
        # Ulanayotgan foydalanuvchini olish
        self.user = self.scope.get('user', AnonymousUser())
        # URL dan group id ni olish
        self.group_id = self.scope['url_route']['kwargs']['pk']

        # Agar foydalanuvchi ulanishni istamagan yoki guruhga kirish huquqi yo'q bo'lsa, ulanishni yopamiz
        if not (await self.is_authenticated() and await self.has_group_access()):
            await self.close()
            return

        # Foydalanuvchini guruhga qo'shish
        await self.channel_layer.group_add(f"group_{self.group_id}", self.channel_name)
        await self.accept()

        # Foydalanuvchini guruhga qo'shish va uning onlayn holatini yangilash
        await self.add_user_to_group()
        await self.update_user_status(is_online=True)
        # Guruhdagi barcha foydalanuvchilarga xabar yuborish
        await self.notify_group_users()
        # Guruhdagi xabarlarni olish
        await self.get_messages(self.group_id)

    async def disconnect(self, code):
        """WebSocket ulanishini uzish."""
        if await self.is_authenticated():
            # Foydalanuvchini guruhdan olib tashlash va uning holatini yangilash
            await self.remove_user_from_group()
            await self.update_user_status(is_online=False)
            # Guruhdagi foydalanuvchilarga xabar yuborish
            await self.notify_group_users()

        # Guruhdan ulanishni uzish
        await self.channel_layer.group_discard(f"group__{self.group_id}", self.channel_name)
        await super().disconnect(code)

    async def notify_group_users(self):
        """Guruh a'zolarini foydalanuvchi holati o'zgarganligi haqida xabardor qilish."""
        group_members = await self.get_group_members()
        await self.channel_layer.group_send(
            f"group__{self.group_id}",
            {
                "type": "update_group_users",
                "users": group_members,
            }
        )

    async def update_group_users(self, event: dict):
        """Guruhdagi foydalanuvchilar ro'yxatini muloqotga yuborish."""
        await self.send_json({'users': event['users']})

    @action()
    async def get_messages(self, pk, **kwargs):
        """ Guruh xabarlarini olish."""
        messages = await self.fetch_group_messages(pk)
        serialized_messages = await self.serialize_messages(messages)

        await self.send_json({
            'action': 'get_messages', 'messages': serialized_messages
        })

    @action()
    async def get_group_messages(self, pk, **kwargs):
        """ Guruhdagi xabarlarni olish va yuborish."""
        messages = await self.fetch_group_messages(pk)
        serialized_messages = await self.serialize_messages(messages)

        await self.send_json({
            'action': 'get_group_messages',
            'messages': serialized_messages,
        })

    @database_sync_to_async
    def get_group(self):
        """ Guruhni ID orqali olish."""
        return Group.objects.filter(pk=self.group_id).first()

    @database_sync_to_async
    def serialize_messages(self, messages):
        """ Xabarlarni serializer orqali yuborish uchun tayyorlash."""
        return GroupMessageSerializer(
            messages, many=True, context={'user': self.user}
        ).data

    @database_sync_to_async
    def get_group_members(self):
        """ Guruh a'zolarini olish."""
        group = self.group
        return [UserSerializer(user).data for user in group.members.all()]

    @database_sync_to_async
    def add_user_to_group(self):
        """ Foydalanuvchini guruhga qo'shish."""
        GroupParticipant.objects.get_or_create(group_id=self.group_id, user=self.user)

    @database_sync_to_async
    def remove_user_from_group(self):
        """ Foydalanuvchini guruhdan olib tashlash."""
        GroupParticipant.objects.filter(group_id=self.group_id, user=self.user).delete()

    @database_sync_to_async
    def fetch_group_messages(self, pk: int):
        """ Guruh xabarlarini olish."""
        group = Group.objects.filter(pk=pk).first()
        if not group:
            return []

        return list(group.groupmessage_set.order_by('sent_at'))

    @database_sync_to_async
    def update_user_status(self, is_online):
        """ Foydalanuvchining onlayn holatini va oxirgi ko'rish vaqtini yangilash."""
        self.user.is_online = is_online
        self.user.update_last_seen()
        self.user.save()

    @database_sync_to_async
    def is_user_group_member(self):
        """ Foydalanuvchi guruh a'zosi yoki emasligini tekshirish."""
        if self.group.owner.id == self.user.id:
            return True
        return self.group.members.filter(id=self.user.id).exists()

    async def is_authenticated(self):
        """ Foydalanuvchini autentifikatsiyadan o'tganligini tekshirish."""
        return self.user.is_authenticated and not isinstance(self.user, AnonymousUser)

    async def has_group_access(self):
        """ Foydalanuvchining guruhga kirish huquqiga ega yoki yo'qligini tekshirish."""
        self.group = await self.get_group()
        if not self.group:
            return False

        if self.group.is_private:
            return await self.is_user_group_member()

        return True

