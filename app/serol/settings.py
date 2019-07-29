# -*- coding: utf-8 -*-
# Django settings for SEROL project.

import os, ast
from django.utils.crypto import get_random_string


VERSION = '0.2'

SITE_ID = 1

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
PRODUCTION = True if CURRENT_PATH.startswith('/var/www') else False
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEBUG= ast.literal_eval(os.environ.get('DEBUG', 'False'))

ALLOWED_HOSTS = ['*']

ADMINS = [('Edward Gomez','egomez@lco.global')]

ADMIN_SITE_HEADER = 'SEROL admin'

# Application definition

CORS_ORIGIN_ALLOW_ALL=True

INSTALLED_APPS = [
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
    'rest_framework.authtoken',
    'storages',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'serol.auth_backend.PortalBackend',
    'serol.auth_backend.AddTokenBackend',
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



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = False

BASE_URL = 'https://serol.lco.global'

STATIC_URL = '/static/'
STATIC_ROOT = '/static/'

MEDIA_URL = '/images/'
MEDIA_ROOT = '/images/'

SECRET_KEY = os.getenv('SECRET_KEY','')
if not SECRET_KEY:
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    SECRET_KEY = get_random_string(50, chars)

# Use AWS S3 for Media Files
if ast.literal_eval(os.environ.get('USE_S3', 'False')):
    # aws settings
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    # s3 public media settings
    PUBLIC_MEDIA_LOCATION = 'media'
    MEDIA_URL = f'https://s3-{AWS_S3_REGION_NAME}.amazonaws.com/{AWS_STORAGE_BUCKET_NAME}/{PUBLIC_MEDIA_LOCATION}/'
    DEFAULT_FILE_STORAGE = 'serol.storage_backends.PublicMediaStorage'

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
            'level': 'ERROR',
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
PORTAL_REQUEST_API = PORTAL_API_URL + 'requestgroups/'
PORTAL_TOKEN_URL   = PORTAL_API_URL + 'api-token-auth/'
PORTAL_PROFILE_URL = PORTAL_API_URL + 'profile/'
ARCHIVE_URL        = 'https://archive-api.lco.global/'
ARCHIVE_FRAMES_URL = ARCHIVE_URL + 'frames/'
ARCHIVE_TOKEN_URL  = ARCHIVE_URL + 'api-token-auth/'

THUMB_SERVICE = 'https://thumbnails.lco.global/{}/?width=4000&height=4000&color=true'

PORTAL_TOKEN = os.environ.get('PORTAL_TOKEN','')
ARCHIVE_TOKEN = os.environ.get('ARCHIVE_TOKEN','')

DEFAULT_CAMERAS = { '1m0' : '1M0-SCICAM-SBIG',
                    '2m0' : '2M0-SCICAM-SPECTRAL',
                    '0m4' : '0M4-SCICAM-SBIG'
                    }
DEFAULT_PROPOSAL = os.environ.get('DEFAULT_PROPOSAL','LCOEPO2018B-002')

COLOUR_TEMPLATE = {'rp':'1','V':'2','B':'3'}


LOGIN_URL = "/accounts/login/"
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
