from django.urls import path
from .views import (SignUpView, VerifyView, LoginView,
                    UserProfileView, UserAvatarUploadView,
                    DeviceListView, LogoutView, ContactAPIView,
                    ContactSyncView, Enable2FAView, Verify2FAView,
                    UserPresenceView, NotificationView)

urlpatterns = [
    path('register/', SignUpView.as_view(), name='signup'),
    path('verify/<str:otp_secret>/', VerifyView.as_view(), name='verify'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('avatars/', UserAvatarUploadView.as_view(), name='user-avatar-upload'),
    path('avatars/<uuid:id>/', UserAvatarUploadView.as_view(), name='user-avatar-upload'),
    path('devices/', DeviceListView.as_view(), name='device-list'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('contacts/', ContactAPIView.as_view(), name='contact-list-create'),
    path('contacts/<uuid:pk>/', ContactAPIView.as_view(), name='contact-delete'),
    path('contacts/sync/', ContactSyncView.as_view(), name='contact-sync'),
    path('2fa/', Enable2FAView.as_view(), name='2-FA'),
    path('2fa/verify/', Verify2FAView.as_view(), name='verify-2fa'),
    path('<uuid:user_id>/status/', UserPresenceView.as_view(), name='user-presence'),
    path('notifications/', NotificationView.as_view(), name='notification-settings'),
]