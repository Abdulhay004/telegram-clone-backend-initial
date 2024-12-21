import uuid
import datetime
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.utils import timezone
from typing import Union
from uuid import UUID
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from share.enums import TokenType
from share.services import TokenService
from .models import User

# redis_conn = redis.StrictRedis(settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)


# ALGORITHM = "HS256"


class UserService:
    @classmethod
    def authenticate(cls, phone_number: str) -> Union[ValidationError, User, None]:
        # Foydalanuvchini tekshirish jarayoni
        user = authenticate(username=phone_number, password=None)
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return user

    @classmethod
    def create_tokens(cls, user: User, access: str = None, refresh: str = None) -> dict[str, str]:
        # Tokenlarni yaratish jarayoni
        if not access or not refresh:
            refresh = RefreshToken.for_user(user)
            access = str(getattr(refresh, "access_token"))
            refresh = str(refresh)
        valid_access_tokens = TokenService.get_valid_tokens(
            user_id=user.id, token_type=TokenType.ACCESS
        )
        if valid_access_tokens:
            TokenService.add_token_to_redis(
                user.id,
                access,
                TokenType.ACCESS,
                settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME")
            )
        valid_refresh_tokens = TokenService.get_valid_tokens(
            user_id=user.id, token_type=TokenType.REFRESH)
        if valid_refresh_tokens:
            TokenService.add_token_to_redis(
                user.id,
                refresh,
                TokenType.REFRESH,
                settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME")
            )

        return {
            "access": access,
            "refresh": refresh
        }
    #
    # @classmethod
    # def get_user_by_email_or_phone(cls, email_or_phone_number: str) -> User:
    #     if User.objects.filter(phone_number=email_or_phone_number).exists():
    #         return User.objects.filter(phone_number=email_or_phone_number).first()
    #     if User.objects.filter(email=email_or_phone_number).exists():
    #         return User.objects.filter(email=email_or_phone_number).first()
    #
    #
    # @classmethod
    # def generate_access_token(cls, user: User) -> str:
    #     payload = {
    #         "sub": str(user.id),
    #         "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    #     }
    #     token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    #     return token
    #
    # @classmethod
    # def generate_refresh_token(cls, user: User) -> str:
    #     payload = {
    #         "sub": str(user.id),
    #         "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
    #     }
    #     token = jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)
    #     return token