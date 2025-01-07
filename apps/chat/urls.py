from django.urls import path
from . import views

from django.views.generic import TemplateView

urlpatterns = [
    path('', views.ChatAPIView.as_view(), name='chat-crud-api'),
    path('<uuid:id>/', views.ChatDetailAPIView.as_view(), name='chat-detail'),
    path('ws/', TemplateView.as_view(template_name='chat/index.html'), name='websocket')
]