from .base import *

SECRET_KEY = 'nhph9jxo%9c3npo7y9oli)=v1r6#fdf!*1*#kbe1uq@09%y&dc'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
INTERNAL_IPS = ['127.0.0.1']
RECAPTCHA_PUBLIC_KEY = None
RECAPTCHA_PRIVATE_KEY = None
