import redis
from django.conf import settings
from django.db import transaction
from unittest.mock import Mock
import uuid

from django.utils.text import phone2numeric
from share.tasks import send_sms_task, send_email_task
from share.utils import generate_otp
from django.utils.translation import gettext_lazy as _

from .serializers import (SignUpSerializer, VerifyOTPSerializer, LoginSerializer,
                          UserProfileSerializer, UserAvatarSerializer, DeviceInfoSerializer,
                          ContactSerializer, TwoFactorAuthSerializer)
from .models import User, UserAvatar, DeviceInfo, Contact
from .services import UserService
from share.services import TokenService
from share.enums import TokenType

import datetime

from share.utils import check_otp

from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework import generics, status, pagination, viewsets
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
        phone_number = request.data.get('phone_number')
        user = User.objects.filter(phone_number=phone_number, is_2fa_enabled=True).first()

        if user:
            return Response({
                "detail": "2FA enabled, please verify your password",
                "user_id": user.id
            }, status=status.HTTP_200_OK)
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

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user_profile = self.get_object()
        if not user_profile.is_verified:
            raise PermissionDenied("Foydalanuvchi tasdiqlanmagan.")
        serializer = self.get_serializer(user_profile)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        user_profile = self.get_object()
        serializer = self.get_serializer(user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        error_message = {'user_name': ['User name cannot be empty.']}
        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

class CustomPagination(pagination.PageNumberPagination):
    page_size = 10

class UserAvatarUploadView(generics.ListCreateAPIView):
    serializer_class = UserAvatarSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UserAvatar.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        user_avatar = self.get_queryset().filter(id=kwargs['id']).first()
        if user_avatar:
            user_avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)

class DeviceListView(generics.ListAPIView):
    serializer_class = DeviceInfoSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return DeviceInfo.objects.filter(user=self.request.user).order_by('-created_at')

class LogoutView(APIView):
    permission_classes = [IsAuthenticated,]
    def post(self,request,*args,**kwargs):
        user = request.user
        TokenService.delete_tokens(user_id=request.user.id,token_type=TokenType.ACCESS)
        TokenService.delete_tokens(user_id=request.user.id,token_type=TokenType.REFRESH)
        TokenService.add_token_to_redis(
            user.id,
            "fake_token",
            TokenType.ACCESS,
            settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
        )

        TokenService.add_token_to_redis(
            user.id,
            "fake_token",
            TokenType.REFRESH,
            settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"],
        )
        return Response(data={"detail":"Successfully logged out"})

class ContactAPIView(generics.ListCreateAPIView, generics.DestroyAPIView):
    queryset = Contact.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ContactSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Contact.objects.filter(user=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionError("You do not have permission to delete this contact.")
        instance.delete()

class ContactSyncView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ContactSerializer

    def create(self, request, *args, **kwargs):
           contacts_data = request.data
           responses = []

           with transaction.atomic():
               for contact_data in contacts_data:
                   phone_number = contact_data.get('phone_number')
                   first_name = contact_data.get('first_name')
                   last_name = contact_data.get('last_name')
                   if Contact.objects.filter(phone_number=phone_number).exists():
                       responses.append({"status": "already exists", "phone_number": phone_number})
                   elif phone_number == request.user.username:
                       responses.append({"status": "self", "phone_number": phone_number})
                   elif first_name+last_name == 'NotFound':
                       responses.append({"status": "not found", "phone_number": phone_number})
                   else:
                       new_contact = Contact.objects.create(user=request.user, **contact_data)
                       responses.append({"status": "created", "phone_number": new_contact.phone_number})

           return Response(responses, status=status.HTTP_201_CREATED)

class Enable2FAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        type_value = request.data.get('type')
        otp_secret = request.data.get('otp_secret')

        if type_value is None:
            return Response({"detail": "Type must be specified."}, status=status.HTTP_400_BAD_REQUEST)

        if type_value == True:
            # 2FA yoqish
            if otp_secret and len(otp_secret) >= 8:
                user.otp_secret = otp_secret
                user.is_2fa_enabled = True
                user.save()
                return Response({"detail": "2FA enabled."}, status=status.HTTP_200_OK)
            else:
                return Response(["OTP secret must be at least 8 characters long."], status=status.HTTP_400_BAD_REQUEST)

        elif type_value == False:
            # 2FA o'chirish
            user.is_2fa_enabled = False
            user.otp_secret = None
            user.save()
            return Response({"detail": "2FA disabled."}, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid type value."}, status=status.HTTP_400_BAD_REQUEST)

class Verify2FAView(generics.GenericAPIView):
    serializer_class = TwoFactorAuthSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        tokens = UserService.create_tokens(user)
        return Response(tokens, status=status.HTTP_200_OK)
