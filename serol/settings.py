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

ADMIN_TITLE = 'SEROL admin'

# Application definition

INSTALLED_APPS = [
    'explorer.apps.ExplorerConfig',
    'status.apps.StatusConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
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

chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
SECRET_KEY = get_random_string(50, chars)

DATABASES = {
    "default": {
        # Live DB
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get('SEROL_DB_NAME', 'seroldb'),
        "USER": os.environ.get('SEROL_DB_USER',''),
        "PASSWORD": os.environ.get('SEROL_DB_PASSWD',''),
        "HOST": os.environ.get('SEROL_DB_HOST',''),
        "CONN_MAX_AGE" : 1800,
        "OPTIONS"   : {'init_command': 'SET storage_engine=INNODB'},

    }
}

PORTAL_API_URL = 'https://observe.lco.global/api/'
PORTAL_REQUEST_API = PORTAL_API_URL + 'userrequests/'
PORTAL_REQUEST_URL = 'https://observe.lco.global/userrequests/'
PORTAL_TOKEN_URL = PORTAL_API_URL + 'api-token-auth/'
PORTAL_TOKEN = os.environ.get('VALHALLA_TOKEN','')

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
