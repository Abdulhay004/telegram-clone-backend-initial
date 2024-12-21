import random
import string
import time
import redis
from django.conf import settings

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






    # if check_if_exists and phone_number in otp_storage:
    #     # Agar OTP mavjud bo'lsa va muddat o'tmagan bo'lsa, qaytarish
    #     stored_otp, timestamp = otp_storage[phone_number]
    #     if time.time() - timestamp < expire_in:
    #         return stored_otp, "OTP already exists and is valid."
    # # Yangi OTP yaratish
    # otp_code = ''.join(random.choices(string.digits, k=6))  # 6 raqamli OTP
    # otp_secret = ''.join(random.choices(string.ascii_letters + string.digits, k=16))  # 16 belgidan iborat sir
    # # Yangilangan OTP va vaqtni saqlash
    # otp_storage[phone_number] = (otp_code, time.time())
    # secret_token = token_urlsafe()
    # redis_conn.set(f"{phone_number}:otp_secret", secret_token, ex=expire_in)
    # return otp_code, otp_secret