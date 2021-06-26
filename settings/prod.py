import os
from project.settings import *  # noqa
import dj_database_url

SECRET_KEY = os.environ['PRODUCTION_KEY']

DATABASES['default'] = dj_database_url.config(conn_max_age=600)
DATABASES['default'] = dj_database_url.config(default=os.environ['DATABASE_URL'])

DEBUG = True

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ALLOWED_HOSTS = ['fantasydrag.herokuapp.com', 'herokuapp.com', ]
