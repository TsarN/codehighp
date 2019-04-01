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

CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Europe/Moscow'

INVOKER_STORE = '/tmp/invoker'
MAX_LOG_FILE_SIZE = 65536
