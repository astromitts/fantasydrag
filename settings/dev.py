import os
from settings import *  # noqa

DEBUG = True

MIDDLEWARE_DEBUG = True

STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), ]
