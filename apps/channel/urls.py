from django.urls import path
from . import views

urlpatterns = [
    path('', views.ChannelListCreateView.as_view(), name='group-list-create'),
    path('<uuid:pk>/', views.ChannelDetailView.as_view(), name='group-detail'),

]