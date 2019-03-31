from .base import *

DEBUG = True

SECRET_KEY = '2wwm*aki$&u!rmjab-(7+e5lm1=o_5c&dr3i%nrydrw$2=sl8s'

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}