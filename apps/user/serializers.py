from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied

from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from share.tasks import send_sms_task, send_email_task
from share.utils import generate_otp
from share.utils import check_otp
import re
from .models import User, UserAvatar, DeviceInfo, Contact, NotificationPreference


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

class UserProfileSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    phone_number = serializers.CharField(read_only=True)
    user_name = serializers.CharField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    birth_date = serializers.DateField(required=False, allow_null=True)
    first_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    last_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = ["id", "phone_number", "user_name", "bio", "birth_date", "first_name", "last_name"]

    def update(self, instance, validated_data):
        instance.user_name = validated_data.get('user_name', instance.user_name)
        instance.bio = validated_data.get('bio', instance.bio)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance

class UserAvatarSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    avatar = serializers.ImageField()
    class Meta:
        model = UserAvatar
        fields = ['id', 'avatar']

    def create(self, validated_data):
       user = validated_data.pop('user')
       user_avatar = UserAvatar.objects.create(user=user, **validated_data)
       return user_avatar

class DeviceInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceInfo
        fields = ['device_name', 'ip_address', 'last_login']

class ContactSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(max_length=20,read_only=True)
    username = serializers.CharField(read_only=True)
    phone = serializers.CharField(max_length=30, write_only=True)
    class Meta:
        model = Contact
        fields = ['id', 'username', 'first_name', 'last_name', 'phone_number', 'phone']
        read_only_fields = ['id', 'username']

    def create(self, validated_data):
       phone_number = validated_data.pop('phone')
       friend = User.objects.filter(phone_number=phone_number).first()
       if not friend:
           raise ValidationError("User Friend Not Found.")
       context = Contact.objects.create(friend=friend, **validated_data)
       return context

class TwoFactorAuthSerializer(serializers.Serializer):
    user_id = serializers.UUIDField()
    password = serializers.CharField(write_only=True)
    otp_code = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = User.objects.filter(id=attrs['user_id']).first()
        if not user:
            raise serializers.ValidationError("User not found.")

        if not user.check_password(attrs['password']):
            raise serializers.ValidationError("Invalid password.")

        if user.is_2fa_enabled and user.otp_secret:
            totp = pyotp.TOTP(user.otp_secret)
            if not totp.verify(attrs['otp_code']):
                raise serializers.ValidationError("Invalid OTP code.")
        else:
            raise serializers.ValidationError("2FA is not enabled for this user.")

        attrs['user'] = user
        return attrs

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = ['id', 'notifications_enabled', 'device_token']