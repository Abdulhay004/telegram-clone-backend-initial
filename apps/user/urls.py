from django.urls import path
from .views import SignUpView, VerifyView, LoginView

urlpatterns = [
    path('register/', SignUpView.as_view(), name='signup'),
    path('verify/<str:otp_secret>/', VerifyView.as_view(), name='verify'),
    path('login/', LoginView.as_view(), name='login'),
]