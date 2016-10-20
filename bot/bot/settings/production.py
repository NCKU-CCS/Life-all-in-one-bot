# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']

MIDDLEWARE += [
    'django.middleware.csrf.CsrfViewMiddleware',
]

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'bot-db',
        'USER': 'bot-user',
        'PASSWORD': 'bot',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
