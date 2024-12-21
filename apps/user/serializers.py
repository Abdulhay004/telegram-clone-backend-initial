from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from share.tasks import send_sms_task, send_email_task
from share.utils import generate_otp
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