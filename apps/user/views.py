from django.shortcuts import render
import redis
from django.conf import settings

from share.utils import generate_otp

from .serializers import SignUpSerializer

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

redis_conn = redis.StrictRedis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)

class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        phone_number = request.data.get('phone_number')
        otp_secret = redis_conn.get(f"{phone_number}:otp_secret").decode()

        return Response({"phone_number":user.get('phone_number'), "otp_secret":otp_secret}, status=status.HTTP_201_CREATED)
