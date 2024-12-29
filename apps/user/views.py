from django.shortcuts import render
import redis
from django.conf import settings
from unittest.mock import Mock
redis_m = Mock()

from share.tasks import send_sms_task, send_email_task
from share.utils import generate_otp
from django.utils.translation import gettext_lazy as _

from .serializers import SignUpSerializer, VerifyOTPSerializer, LoginSerializer
from .models import User
from .services import UserService

from share.utils import check_otp

from rest_framework.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
import logging
logger = logging.getLogger(__name__)

redis_conn = redis.StrictRedis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)

class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    queryset = User.objects.all()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        phone_number = serializer.validated_data.get('phone_number')
        otp_secret = redis_conn.get(f"{phone_number}:otp_secret").decode()
        data = {
            "phone_number":phone_number,
            "otp_secret":otp_secret
        }
        return Response(data=data,status=status.HTTP_201_CREATED)

class VerifyView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer
    permission_classes = [AllowAny,]
    def patch(self, request, otp_secret):
        data = {'otp_code':request.data.get('otp_code'),
                'phone_number':request.data.get('phone_number'),
                'otp_secret':otp_secret}
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']

        try:
            user = User.objects.filter(phone_number=phone_number).first()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        if user.is_verified:
            return Response({"detail": _("User is already verified.")}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.save()
        tokens = UserService.create_tokens(user)

        return Response(tokens, status=status.HTTP_200_OK)

class LoginView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = LoginSerializer
    permission_classes = [AllowAny,]
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data.get('phone_number')
        user = serializer.save()
        otp_secret = redis_conn.get(f"{user.phone_number}:otp_secret").decode()
        data = {
            "phone_number":phone_number,
            "otp_secret":otp_secret
        }
        return Response(data=data)
