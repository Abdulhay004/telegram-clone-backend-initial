from django.urls import path
from chat.consumers import ChatConsumer
from group.consumers import GroupConsumer

websocket_urlpatterns = [
    path('ws/chats/<uuid:pk>/', ChatConsumer.as_asgi()),
    path('ws/groups/<uuid:pk>/', GroupConsumer.as_asgi()),
]