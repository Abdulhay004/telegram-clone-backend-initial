from django.urls import path
from . import views

urlpatterns = [
    path('', views.ChatAPIView.as_view(), name='chat-crud-api'),
    path('<uuid:id>/', views.ChatDetailAPIView.as_view(), name='chat-detail'),
]