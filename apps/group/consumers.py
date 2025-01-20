from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from djangochannelsrestframework.generics import GenericAsyncAPIConsumer
from djangochannelsrestframework.observer.generics import action
from django.contrib.auth.models import AnonymousUser
import json

from .models import Group, GroupParticipant, User, GroupMessage, GroupPermission
from .serializers import GroupMessageSerializer, UserSerializer

# GroupConsumer Websocket uchun ishlaydigan Consumer bo'lib,guruhdagi foydalanuvchilarni boshqaradi.
class GroupConsumer(GenericAsyncAPIConsumer,AsyncJsonWebsocketConsumer):
    queryset = Group.objects.all()
    serializer_class = GroupMessageSerializer # Faqat messagelar uchun ishlatiladi
    lookup_field = 'pk'

    async def connect(self):
        """Websocket ulanishini boshqarish"""
        # Ulanayotgan foydalanuvchini olish
        self.user = self.scope.get("user",AnonymousUser())

        # Url dan guruh ID sini olish
        self.group_id = self.scope["url_route"]["kwargs"]["pk"]

        # Agar foydalanuvchi authentifikatsiyadan o'tmagan yoki guruhga kirishga huquqi yo'q bo'lsa ulanishni yopamiz
        if not (await self.is_authenticated() and await self.has_group_access()):
            await self.close()
            return

        # Foydalanuvchini guruhga qo'shish
        await self.channel_layer.group_add(f"group__{self.group_id}",self.channel_name)
        #Ulanishni qabul qilish
        await self.accept()

        # Foydalanuchini guruhga qo'shish va uni holatini o'zgartirish
        await self.add_user_to_group()
        await self.update_user_status(is_online=True)

        # Guruhdagi barcha foydalanuvchilarga habar yuboramiz
        await self.notify_group_users()
        # Guruhdagi barcha habarlarni olish
        await self.get_messages(self.group_id)

    async def disconnect(self, code):
        """WebSocket ulanishini yopish"""
        if await self.is_authenticated():
            # Foydalanuvchini guruhdan olib tashlash
            await self.remove_user_from_group()
            await self.update_user_status(is_online=False)
            # Guruhdagi foydalanuvchilarga habar yuborish
            await self.notify_group_users()

        await self.channel_layer.group_discard(f"group__{self.group_id}",self.channel_name)
        await super().disconnect(code)

    async def notify_group_users(self):
        """Guruh a'zolarini foydalanuvchi holati o'zgarganini habar berish"""
        group_members = await self.get_group_members()
        await self.channel_layer.group_send(
            f"group__{self.group_id}",
            {
                "type":"update_group_users",
                "users":group_members
            }
        )

    async def update_group_users(self,event:dict):
        """Guruhdagi foydalanuchilar ro'yhatini mijozga yuborish"""
        await self.send_json({"users":event['users']})

    @action()
    async def get_messages(self,pk,**kwargs):
        """Guruh habarlarini olish"""
        messages = await self.fetch_group_messages(pk)
        serialized_messages = await self.serialize_messages(messages)
        await self.send_json(
            {"action":"get_messages","messages":serialized_messages}
        )

    @action()
    async def get_group_messages(self,pk,**kwargs):
        """Guruhdagi habarlarni olish va yuborish"""
        messages = await self.fetch_group_messages(pk)
        serialized_messages = await self.serialize_messages(messages)
        await self.send_json(
            {"action": "get_group_messages", "messages": serialized_messages}
        )

    @database_sync_to_async
    def get_group(self):
        """Guruhni ID orqali olish"""
        return Group.objects.filter(pk=self.group_id).first()

    @database_sync_to_async
    def serialize_messages(self,messages):
        return GroupMessageSerializer(
            messages,many=True,context={"user":self.user}
        ).data

    @database_sync_to_async
    def get_group_members(self):
        """Guruh a'zolarini olish."""
        group = self.group
        return [UserSerializer(user).data for user in group.members.all()]

    @database_sync_to_async
    def add_user_to_group(self):
        """Foydalanuvchini guruhga qo'shish"""
        GroupParticipant.objects.get_or_create(group_id=self.group_id,user=self.user)



    @database_sync_to_async
    def remove_user_from_group(self):
        """Foydalanuvchini guruhdan olib tashlash"""
        GroupParticipant.objects.filter(group_id=self.group_id,user=self.user).delete()

    @database_sync_to_async
    def fetch_group_messages(self,pk:int):
        """Guruh habarlarini olish"""
        group = Group.objects.filter(pk=pk).first()
        if not group:
            return []
        return list(group.messages.order_by("sent_at"))

    @database_sync_to_async
    def update_user_status(self,is_online):
        """Foydalanuvchi onlayn holatini va ohirgi ko'rish vaqtini yangilash"""
        self.user.is_online = is_online
        self.user.update_last_seen()
        self.user.save()

    @database_sync_to_async
    def is_user_group_member(self):
        """Foydalanuvchi guruh a'zosi yoki emasligini tekshirish"""
        if self.group.owner.id ==self.user.id:
            return True
        return self.group.members.filter(id=self.user.id).exists()

    async def is_authenticated(self):
        """Foydalanuvchi authentifikatsiyadan o'tganligini tekshirish"""
        return self.user.is_authenticated and not isinstance(self.user,AnonymousUser)

    async def has_group_access(self):
        """Foydalanuvchi guruhga kirish yoki yo'qlini aniqlash"""
        self.group = await self.get_group()
        if not self.group:
            return False

        if self.group.is_private:
            return await self.is_user_group_member()

        return True

    @database_sync_to_async
    def can_send_message(self,pk):
        group_permission = GroupPermission.objects.filter(group_id=pk).first()
        return group_permission.can_send_messages

    # habar yuborish fuksiyasi
    @action()
    async def create_message(self,pk,data,**kwargs):
        """Yangi habar yaratish va uni guruh a'zolariga tarqatish"""

        #agar foydalanuvchi guruh a'zosi bo'lmasa
        if not await self.is_user_group_member():
            await self.send_json(
                {"detail":"You are not a member of this group. Please join first."}
            )
            return

        # Agar foydalanuvchi habar yuborish huquqi bo'lmasa
        if not await self.can_send_message(self.group_id):
            await self.send_json(
                {"detail":"Sizning habar yuborish huquqingiz yo'q."}
            )
            return

        #Xabarni saqlash
        message = await self.save_message(self.group,self.user,data)
        serialized_message = await self.serialize_message(message)

        await self.channel_layer.group_send(
            f"group__{pk}",
            {
                "type":"group_message",
                "text":serialized_message
            }
        )

    # Xabarni qabul qiluvchi handler
    async def group_message(self, event):
        """Guruhdagi xabarni mijozlarga yuborish"""
        text = event.get("text", {})
        print(text)
        await self.send_json({"action": "new_message", "data": text})

    @database_sync_to_async
    def save_message(self,group:Group,user:User,data:dict):
        """Guruhga yangi habarni saqlash"""
        valid_keys = {"text","image","file"}
        message_data = {key:data.get(key) for key in valid_keys if data.get(key)}
        return GroupMessage.objects.create(group=group,sender=user,**message_data)

    @database_sync_to_async
    def serialize_message(self,message):
        return GroupMessageSerializer(message).data


