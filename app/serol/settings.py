# -*- coding: utf-8 -*-
# Django settings for SEROL project.

import os, sys
from django.utils.crypto import get_random_string

VERSION = '0.1'

SITE_ID = 1

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
PRODUCTION = True if CURRENT_PATH.startswith('/var/www') else False
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG=False

ALLOWED_HOSTS = ['*']

ADMIN_SITE_HEADER = 'SEROL admin'

# Application definition

CORS_ORIGIN_ALLOW_ALL=True

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'highscore.apps.HighscoreConfig',
    'explorer.apps.ExplorerConfig',
    'status.apps.StatusConfig',
    'stickers.apps.StickersConfig',
    'notify.apps.NotifyConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'pagedown',
    'markdown_deux',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'serol.auth_backend.ValhallaBackend',
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
STATIC_ROOT = '/var/www/html/static/'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/images/'

MEDIA_ROOT = '/var/www/html/images/'

IMAGE_ROOT = MEDIA_ROOT

SECRET_KEY = os.environ.get('SECRET_KEY','')
if not SECRET_KEY:
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    SECRET_KEY = get_random_string(50, chars)

DATABASES = {
    "default": {
        # Live DB
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ.get('DB_NAME', ''),
        "USER": os.environ.get('DB_USER',''),
        "PASSWORD": os.environ.get('DB_PASS',''),
        "HOST": os.environ.get('DB_HOST','mysql'),
        "PORT"   : '3306',

    }
}

ACCOUNT_ACTIVATION_DAYS = 28

#############
# Email
############

EMAIL_USE_TLS       = True
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          =  587
EMAIL_FROM  = 'Serol <portal@lco.global>'
EMAIL_HOST_USER = os.environ.get('EMAIL_USERNAME', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')

MARKDOWN_DEUX_STYLES = {
    "default": {
        "extras": {
            "code-friendly": None,
        },
        "safe_mode": False,
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'DEBUG',
        }
    },
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework_jsonp.renderers.JSONPRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}



PORTAL_API_URL     = 'https://observe.lco.global/api/'
PORTAL_REQUEST_SUBMIT_API = PORTAL_API_URL + 'userrequests/'
PORTAL_REQUEST_API = PORTAL_API_URL + 'requests/'
PORTAL_TOKEN_URL   = PORTAL_API_URL + 'api-token-auth/'
PORTAL_PROFILE_URL = PORTAL_API_URL + 'profile/'
ARCHIVE_URL        = 'https://archive-api.lco.global/'
ARCHIVE_FRAMES_URL = ARCHIVE_URL + 'frames/'
ARCHIVE_TOKEN_URL  = ARCHIVE_URL + 'api-token-auth/'

PORTAL_TOKEN = os.environ.get('PORTAL_TOKEN','')
ARCHIVE_TOKEN = os.environ.get('ARCHIVE_TOKEN','')

DEFAULT_CAMERAS = { '1m0' : '1M0-SCICAM-SBIG',
                    '2m0' : '2M0-SCICAM-SPECTRAL',
                    '0m4' : '0M4-SCICAM-SBIG'
                    }
DEFAULT_PROPOSAL = 'LCOEPO2014B-010'

COLOUR_TEMPLATE = {'rp':'1','V':'2','B':'3'}


LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

PROGRESS_OPTIONS =  (
                ('New','New'),
                ('Submitted', 'Submitted'),
                ('Observed','Observed'),
                ('Identify','Identify'),
                ('Analyse','Analyse'),
                ('Investigate','Investigate'),
                ('Summary','Summary'),
                ('Failed','Failed')
                )

FILTER_ORDER = {
            'jupiter'   : {'up':1,'B':2,'zs':3},
            'mars'      : {},
            'saturn'    : {'zs':1}
                }

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
