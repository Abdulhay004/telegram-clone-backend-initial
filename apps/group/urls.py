from django.urls import path
from . import views

urlpatterns = [
    path('', views.GroupListCreateView.as_view(), name='group-list-create'),
    path('<uuid:pk>/', views.GroupDetailView.as_view(), name='group-detail'),
    path('<uuid:pk>/permissions/', views.GroupPermissionsUpdateView.as_view(), name='group-permissions-update'),
    path('<uuid:group_id>/memberships/', views.GroupMembershipsView.as_view(), name='group-memberships'),
    path('<uuid:id>/members/', views.GroupMembersView.as_view(), name='group-members'),
    path('<uuid:pk>/messages/', views.GroupMessageView.as_view(), name='group-messages'),
]