import random
import string
import time
import redis
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.utils.translation import gettext_lazy as _

from secrets import token_urlsafe
from django.contrib.auth.hashers import check_password, make_password
from rest_framework.exceptions import ValidationError

redis_conn = redis.StrictRedis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)

otp_storage = {}

def generate_otp(phone_number: str,
                 expire_in: int = 120,
                 check_if_exists: bool=True):
    otp_code = "".join(random.choices(string.digits, k=6))
    secret_token = token_urlsafe()
    redis_conn.set(f'{phone_number}:otp_secret', secret_token, ex=expire_in)
    otp_hash = make_password(f'{secret_token}:{otp_code}')
    key = f'{phone_number}:otp'
    if check_if_exists:
        if redis_conn.exists(key):
            ttl = redis_conn.ttl(key)
            raise ValidationError(
                f'You have a valid OTP code. Please try again {ttl} seconds', 400
            )
    else:
        redis_conn.delete(key)

    redis_conn.set(key, otp_hash, ex=expire_in)
    return otp_code, secret_token



def check_otp(phone_number: str, otp_code: str, otp_secret: str) -> None:
    stored_hash: bytes = redis_conn.get(f"{phone_number}:otp")
    if not stored_hash or not check_password(
        f"{otp_secret}:{otp_code}", stored_hash.decode()
    ):
        raise ValidationError(_("Invalid OTP code."), 400)


