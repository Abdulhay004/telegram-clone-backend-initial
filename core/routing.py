from django.urls import path
from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/chats/<uuid:pk>/', ChatConsumer.as_asgi())
]