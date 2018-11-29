from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
DEBUG_TOOLBAR = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'nhph9jxo%9c3npo7y9oli)=v1r6#fdf!*1*#kbe1uq@09%y&dc'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
INTERNAL_IPS = ['127.0.0.1']

if DEBUG_TOOLBAR:
    INSTALLED_APPS += ['debug_toolbar', ]
    MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware', ]

try:
    from .local import *
except ImportError:
    pass
