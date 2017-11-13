# -*- coding: utf-8 -*-
# Django settings for SEROL project.

import os, sys
from django.utils.crypto import get_random_string

VERSION = '0.1'

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
PRODUCTION = True if CURRENT_PATH.startswith('/var/www') else False
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG=False

ALLOWED_HOSTS = ['*']

ADMIN_SITE_HEADER = 'SEROL admin'

# Application definition

INSTALLED_APPS = [
    'explorer.apps.ExplorerConfig',
    'status.apps.StatusConfig',
    'stickers.apps.StickersConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'serol.auth_backend.ValhallaBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_USER_MODEL = 'status.User'

ROOT_URLCONF = 'serol.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'serol.wsgi.application'


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = '/var/www/html/'

MEDIA_URL = '/media/'

MEDIA_ROOT = '/var/www/html/media/'

chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
SECRET_KEY = get_random_string(50, chars)

DATABASES = {
    "default": {
        # Live DB
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get('SEROL_DB_NAME', ''),
        "USER": os.environ.get('SEROL_DB_USER',''),
        "PASSWORD": os.environ.get('SEROL_DB_PASSWD',''),
        "HOST": os.environ.get('SEROL_DB_HOST',''),
        "PORT"   : '5432',

    }
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework_jsonp.renderers.JSONPRenderer',
    ),
}

PORTAL_API_URL = 'https://observe.lco.global/api/'
PORTAL_REQUEST_API = PORTAL_API_URL + 'userrequests/'
PORTAL_TOKEN_URL = PORTAL_API_URL + 'api-token-auth/'
PORTAL_PROFILE_URL = PORTAL_API_URL + 'profile/'
ARCHIVE_TOKEN_URL = 'https://archive-api.lco.global/api-token-auth/'

DEFAULT_CAMERAS = { '1m0' : '1M0-SCICAM-SBIG',
                    '2m0' : '2M0-SCICAM-SPECTRAL',
                    '0m4' : '0M4-SCICAM-SBIG'
                    }

PROPOSAL_CODE = 'LCOEPO2014B-010'

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

PROGRESS_OPTIONS =  (
                ('New','New'),
                ('Submitted', 'Submitted'),
                ('Observed','Observed'),
                ('Failed','Failed'),
                ('Retry','Retry'),
                ('Completed','Completed'),
                ('Identify','Identify'),
                ('Analyse','Analyse'),
                ('Identify','Identify'),
                ('Investigate','Investigate')
                )

##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.
if not CURRENT_PATH.startswith('/var/www'):
    try:
        from .local_settings import *
    except ImportError as e:
        if "local_settings" not in str(e):
            raise e
