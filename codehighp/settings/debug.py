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

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REDIS = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0
}

MAX_LOG_FILE_SIZE = 65536

INSTALLED_APPS.append('debug_toolbar')
MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ['127.0.0.1']

GIT_SERVICE_URL = 'https://git.tsarn.website:7443'
GIT_SERVICE_PASSWORD = '5JzGmmvNL40xDis5exx1XoWa5WJSChE3'
GIT_REPO_URL = 'git@git.tsarn.website'

MATHOID_URL = 'http://127.0.0.1:10044'

MAIN_WATCHDOG = None
