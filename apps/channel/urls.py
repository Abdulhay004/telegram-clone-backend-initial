from django.urls import path
from . import views

from .views import MessageViewSet

message_list = MessageViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

message_detail = MessageViewSet.as_view({
    'get': 'retrieve',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', views.ChannelListCreateView.as_view(), name='group-list-create'),
    path('<uuid:pk>/', views.ChannelDetailView.as_view(), name='group-detail'),
    path('<uuid:channel_id>/memberships/', views.MembershipListCreateView.as_view(), name='membership-list-create'),
    path('<uuid:channel_id>/memberships/<uuid:pk>/', views.MembershipDetailView.as_view(), name='membership-detail'),
    path('<uuid:channel_id>/messages/', message_list, name='message-list'),
    path('<uuid:channel_id>/messages/<uuid:message_id>/', message_detail, name='message-detail'),
    path('<uuid:channel_id>/messages/schedule/', views.ScheduleMessageView.as_view(), name='schedule-message'),
    path('<uuid:channel_id>/messages/<uuid:message_id>/like/', views.LikeRemoveMessageView.as_view(), name='like_and_remove_message'),
]