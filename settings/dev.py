import os
from settings import *  # noqa
import dj_database_url

DEBUG = True

MIDDLEWARE_DEBUG = True

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]

DATABASES['default'] = dj_database_url.config()
DATABASES['default'] = dj_database_url.config(conn_max_age=600)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': 'localhost',
        'PORT': '5432',
        'NAME': 'fantasydrag',
        'USER': 'bomorin-id',
        'PASSWORD': '',
    }
}

SENDGRID_API_KEY = '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'
