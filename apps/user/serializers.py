from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from share.tasks import send_sms_task, send_email_task
from share.utils import generate_otp
from share.utils import check_otp
import re
from .models import User

class SignUpSerializer(serializers.Serializer):
    phone_number = serializers.CharField(min_length=9,max_length=16,help_text="telefon raqam")

    def validate_phone_number(self,phone_number):
        pattern = r"^\+?[1-9]\d{1,16}$"
        if re.match(pattern,phone_number):
            if User.objects.filter(phone_number=phone_number,is_verified=True).exists():
                raise ValidationError(_("User with this phone number already exists"))
            return phone_number
        raise ValidationError(_("Phone number not is valid"))

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        user = User.objects.get_or_create(**validated_data)
        otp_code,otp_secret = generate_otp(phone_number=phone_number,expire_in=2*60, check_if_exists=False)
        send_email_task.delay(email="tolibjonovabdulhay200@gmail.com",otp_code=otp_code)
        return user

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True)
    otp_secret = serializers.CharField(required=True)

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        otp_code = attrs.get('otp_code')
        otp_secret = attrs.get('otp_secret')

        check_otp(phone_number, otp_code, otp_secret)

        if not self.is_valid_phone_number(phone_number):
            raise serializers.ValidationError("Noto'g'ri telefon raqami.")

        if not self.is_valid_otp_code(otp_code):
            raise serializers.ValidationError("Noto'g'ri OTP kodi.")

        return attrs

    def is_valid_phone_number(self, phone_number):
        pattern = r"^\+?[1-9]\d{1,16}$"
        if re.match(pattern,phone_number):
            if User.objects.filter(phone_number=phone_number,is_verified=True).exists():
                raise ValidationError(_("User with this phone number already exists"))
            return phone_number
        raise ValidationError(_("Phone number not is valid"))

    def is_valid_otp_code(self, otp_code):
        if len(otp_code) == 6:
            return True
        return False

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, phone_number):
        pattern = r"^\+?[1-9]\d{1,16}$"
        if re.match(pattern, phone_number):
            return phone_number
        raise ValidationError(_("Phone number not is valid"))

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        user = get_object_or_404(User, phone_number=phone_number)
        otp_code,otp_secret = generate_otp(phone_number=phone_number,expire_in=2*60, check_if_exists=False)
        send_email_task.delay(email="tolibjonovabdulhay200@gmail.com",otp_code=otp_code)
        # send_sms_task.delay(phone_number, otp_code)

        return user