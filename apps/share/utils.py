import random
import string
import time
import redis
from django.conf import settings

from unittest.mock import Mock
redis_conn_m = Mock()

from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError

redis_conn = redis.StrictRedis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)

otp_storage = {}

def generate_otp(phone_number: str,
                 expire_in: int = 120,
                 check_if_exists: bool=True) -> tuple[str, str]:
    otp_code = ''.join(random.choices(string.digits, k=6))
    secret_token = get_random_string(32)
    key = f'{phone_number}:otp'

    if check_if_exists:
        if redis_conn.exists(key):
            ttl = redis_conn.ttl(key)
            raise ValidationError(
                f'You have a valid OTP code. Please try again {ttl} seconds', 400
            )
    else:
        redis_conn.delete(key)

    redis_conn.set(f'{phone_number}:otp_secret', secret_token, ex=expire_in)
    otp_hash = make_password(f'{secret_token}:{otp_code}')
    redis_conn.set(key, otp_hash, ex=expire_in)

    return otp_code, secret_token


def check_otp(phone_number: str, otp_code: str, otp_secret: str) -> None:
    # # Redis'dan ma'lumotlarni olish uchun mock qilish
    # redis_conn.get.side_effect = lambda key: {
    #     f"{phone_number}:otp": otp_code,
    #     f"{phone_number}:otp_secret": otp_secret
    # }.get(key)
    stored_otp = redis_conn.get(f"{phone_number}:otp")
    stored_secret = redis_conn.get(f"{phone_number}:otp_secret")

    if stored_otp is None or stored_secret is None:
        raise ValueError("OTP yoki maxfiy kalit topilmadi.")

    stored_otp = stored_otp.decode('utf-8')
    stored_secret = stored_secret.decode('utf-8')

    # Taqqoslash
    if stored_otp != otp_code or stored_secret != otp_secret:
        raise ValueError("OTP kod yoki maxfiy kalit noto'g'ri.")

