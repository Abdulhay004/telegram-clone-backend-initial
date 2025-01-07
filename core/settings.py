import os
import sys
from datetime import timedelta, datetime

import sentry_sdk
import logging
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from pathlib import Path
from django.utils.translation import gettext_lazy as _
from decouple import config


SENTRY_SDK="https://43f88d64a18e48a7307150c375c4b55e@o4508489036201984.ingest.us.sentry.io/4508489040396288"
# BASE
# --------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(os.path.join(BASE_DIR, "apps"))

# SECURITY
# -----------------------------------------------------------------------------------------

SECRET_KEY = "django-insecure-z#9g^u)aoa1*+i#_mpt8&%&wm$4vg6)k(=h++$ftljnbds^1)m"

DEBUG = True

ALLOWED_HOSTS = []

# APPS
# -----------------------------------------------------------------------------------------

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

EXTERNAL_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'django_redis',
    # 'drf_yasg',
    'django_celery_beat',
    'debug_toolbar',
    'channels',
]

LOCAL_APPS = [
    'user',
    'chat',
]

INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + LOCAL_APPS

# MIDDLEWARE
# -----------------------------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "user.middleware.TrackLoginActivityMiddleware",
]

INTERNAL_IPS = [
    '127.0.0.1',
]

ROOT_URLCONF = "core.urls"

# TEMPLATES
# -----------------------------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# APPLICATIONS
# -----------------------------------------------------------------------------------------

# WSGI_APPLICATION = "core.wsgi.application"
ASGI_APPLICATION = "core.asgi.application"

# DATABASES
# -----------------------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# DATABASES = {
#     'default': {
#         'ENGINE': config('DB_ENGINE', default='django.db.backends.sqlite3'),
#         'NAME': config('DB_NAME', default='db.sqlite3'),
#         'USER': config('DB_USER', default=''),
#         'PASSWORD': config('DB_PASSWORD', default=''),
#         'HOST': config('DB_HOST', default=''),
#         'PORT': config('DB_PORT', default=''),
#     }
# }
# PASSWORD VALIDATORS
# -----------------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# INTERNATIONALIZATION
# -----------------------------------------------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

LANGUAGES = [
    ('en', _('English')),
    ('uz', _('Uzbek')),
    ('ru', _('Russian')),
]

MODELTRANSLATION_LANGUAGES = ('en', 'uz', 'ru',)
MODELTRANSLATION_DEFAULT_LANGUAGE = 'uz'

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale/'),
]

# STATIC & MEDIA FILES
# -----------------------------------------------------------------------------------------

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# DEFAULT PRIMARY KEY FIELD
# -----------------------------------------------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# AUTH_USER_MODEL
# -----------------------------------------------------------------------------------------
AUTH_USER_MODEL = 'user.User'

# REST_FRAMEWORK
# -----------------------------------------------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'user.authentications.CustomJWTAuthentication',
        'user.authentications.CustomBasicAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day', # anonim user uchun kuniga 100 ta sms ga ruhsat
        'user': '1000/day', # user uchun kuniga 1000 ta sms ga ruhsat
    }
}

# JWT
# -----------------------------------------------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=10),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JSON_ENCODER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=10),
}

# DRF_SPECTACULAR
# -----------------------------------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    'TITLE': 'Telegram',
    'DESCRIPTION': 'Telegram Clone project',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
}

# REDIS
# -----------------------------------------------------------------------------------------
REDIS_HOST = config('REDIS_HOST', default='localhost')
REDIS_PORT = config('REDIS_PORT', default='6379')
REDIS_DB = config('REDIS_DB', default='1')

REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# CACHES
# -----------------------------------------------------------------------------------------
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}


# CHANNELS
# -----------------------------------------------------------------------------------------
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_URL],
        }
    }
}

# CELERY
# -----------------------------------------------------------------------------------------
if USE_TZ:
    CELERY_TIMEZONE = 'Asia/Tashkent'

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_RESULT_EXTENDED = True
CELERY_RESULT_BACKEND_ALWAYS_RETRY = True
CELERY_RESULT_BACKEND_MAX_RETRIES = 10
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_WORKER_SEND_TASK_EVENTS = True


# SENTRY SDK
# -----------------------------------------------------------------------------------------
# SENTRY_SDK = config("SENTRY_SDK")

sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.ERROR,
)

integrations = [
    sentry_logging,
    DjangoIntegration()
]

sentry_sdk.init(
    dsn=SENTRY_SDK,
    integrations=integrations,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

# FIREBASE
# -----------------------------------------------------------------------------------------


# SMS API
# -----------------------------------------------------------------------------------------


# EMAIL
# -----------------------------------------------------------------------------------------
EMAIL_BACKEND = config('EMAIL_BACKEND', default='')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default='')
EMAIL_PORT = config('EMAIL_PORT', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

# ELASTICSEARCH
# -----------------------------------------------------------------------------------------


# LOGGING
# -----------------------------------------------------------------------------------------
