from django.urls import path
from . import views

urlpatterns = [
    path('', views.ChannelListCreateView.as_view(), name='group-list-create'),
    path('<uuid:pk>/', views.ChannelDetailView.as_view(), name='group-detail'),
    path('<uuid:channel_id>/memberships/', views.MembershipListCreateView.as_view(), name='membership-list-create'),
    path('<uuid:channel_id>/memberships/<uuid:pk>/', views.MembershipDetailView.as_view(), name='membership-detail'),
]