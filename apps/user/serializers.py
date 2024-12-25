from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from share.tasks import send_sms_task, send_email_task
from share.utils import generate_otp
from share.utils import check_otp
from .models import User

class SignUpSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField()

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number']

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')

        try:
            otp_code, otp_secret = generate_otp(phone_number, expire_in=2*60)
        except ValidationError as e:
            raise ValidationError(str(e))

        send_email_task(otp_code)
        send_sms_task(phone_number, otp_code)

        return {
            'phone_number': phone_number,
            'otp_secret': otp_secret
        }

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True)
    # otp_secret = serializers.CharField(required=True)

    def validate(self, attrs):
        # phone_number = attrs.get('phone_number')
        # otp_code = attrs.get('otp_code')
        # otp_secret = attrs.get('otp_secret')
        # check_otp(phone_number, otp_code, otp_secret)

        return attrs

    # def validate(self, attrs):
    #     # Telefon raqami va OTP kodini tekshirish
    #     phone_number = attrs.get('phone_number')
    #     otp_code = attrs.get('otp_code')
    #
    #     # Telefon raqami formatini tekshirish (agar kerak bo'lsa)
    #     if not self.is_valid_phone_number(phone_number):
    #         raise serializers.ValidationError("Noto'g'ri telefon raqami.")
    #
    #     # OTP kodini tekshirish (agar kerak bo'lsa)
    #     if not self.is_valid_otp_code(otp_code):
    #         raise serializers.ValidationError("Noto'g'ri OTP kodi.")
    #
    #     return attrs
    #
    # def is_valid_phone_number(self, phone_number):
    #     if phone_number[0] == '+' and len(phone_number[1:]) == 12:
    #         return True
    #     else:
    #         return False
    #
    # def is_valid_otp_code(self, otp_code):
    #     if len(otp_code) == 6:
    #         return True
    #     else:
    #         return False