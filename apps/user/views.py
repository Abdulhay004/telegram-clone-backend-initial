from django.shortcuts import render
import redis
from django.conf import settings
from unittest.mock import Mock
redis_m = Mock()

from share.utils import generate_otp
from django.utils.translation import gettext_lazy as _

from .serializers import SignUpSerializer, VerifyOTPSerializer
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
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        #check for phone number
        phone_number = request.data.get('phone_number')
        if phone_number is None or \
            len(phone_number) < 10 or \
            phone_number.isalpha():
            return Response({"detail": "Invalid phone number or Required phone number."}, status=400)
        if User.objects.filter(is_verified=True).exists():
            return Response({"detail":"Phone number already exist."}, status=400)

        otp_code, otp_secret = generate_otp(
                phone_number=phone_number,
                expire_in=2 * 60,
                check_if_exists=False
            )

        # OTP secret ni Redisga saqlash
        if redis_conn is None:
               return Response({"redis_conn is not initialized."})
        else:
            redis_conn.setex(phone_number, 120, otp_secret)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        phone_number = request.data.get('phone_number')
        otp_secret = redis_conn.get(f"{phone_number}:otp_secret").decode()

        return Response({"phone_number":user.get('phone_number'), "otp_secret":otp_secret}, status=status.HTTP_201_CREATED)

class VerifyView(APIView):
    serializer_class = VerifyOTPSerializer
    def patch(self, request, otp_secret):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone_number = serializer.validated_data['phone_number']
        otp_code = serializer.validated_data['otp_code']

        try:
            user = User.objects.filter(phone_number=phone_number).first()
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


        if not user:
            return Response({"detail": "Foydalanuvchi topilmadi."}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_verified:
            return Response({"detail": _("User is already verified.")}, status=status.HTTP_400_BAD_REQUEST)
        try:
            check_otp(phone_number, otp_code, otp_secret)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.save()

        redis_conn.delete(f"{phone_number}:otp_secret")
        redis_conn.delete(f"{phone_number}:otp")

        tokens = UserService.create_tokens(user)

        return Response(tokens, status=status.HTTP_200_OK)