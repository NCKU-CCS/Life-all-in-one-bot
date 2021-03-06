from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

MIDDLEWARE += []

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bot_db',
        'USER': 'bot_user',
        'PASSWORD': 'bot',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
