import os
import sys
from decimal import Decimal

import environ
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from social_core.pipeline import DEFAULT_AUTH_PIPELINE

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
env = environ.Env()
TESTING = "pytest" in sys.modules
if not TESTING:
    environ.Env.read_env(os.path.join(os.path.dirname(PROJECT_DIR), '.env'))

DEBUG = env.bool('DEBUG', False)
DEBUG_TOOLBAR = env.bool('DEBUG_TOOLBAR', False)

SENTRY_DSN = env.str("SENTRY_DSN", None)
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()]
    )

BASE_DIR = os.path.dirname(PROJECT_DIR)

INSTALLED_APPS = [
    'home',
    'crm',
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.contrib.modeladmin',
    'wagtail.contrib.settings',
    "wagtail.contrib.table_block",
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail.core',
    'wagtailfontawesome',
    'wagtailmarkdown',
    'wagtailautocomplete',

    'snowpenguin.django.recaptcha2',
    'modelcluster',
    'taggit',
    'colorful',
    'storages',
    'wagtail_storages',
    'ajax_select',
    'wkhtmltopdf',
    'analytical',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'django_fsm_log',
    'social_django',
    'django_extensions',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',

    'whitenoise.middleware.WhiteNoiseMiddleware',
    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default="*")
INTERNAL_IPS = ['127.0.0.1']

if DEBUG_TOOLBAR:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE = MIDDLEWARE + ['debug_toolbar.middleware.DebugToolbarMiddleware']

ROOT_URLCONF = 'freeturn.urls'

CACHE_TEMPLATES = env.bool('CACHE_TEMPLATES', False)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': not CACHE_TEMPLATES,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'context_processors.menu_items'
            ],
            **({'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ], } if CACHE_TEMPLATES else {})
        },
    },
]
WSGI_APPLICATION = 'freeturn.wsgi.application'

SECRET_KEY = env.str('SECRET_KEY')
DEFAULT_SQLITE_PATH = os.path.join(PROJECT_DIR, 'db.sqlite3')
DATABASES = {
    'default': env.db(default=f'sqlite:///{DEFAULT_SQLITE_PATH}'),
    'extra': env.db('SQLITE_URL', default=f'sqlite:///{DEFAULT_SQLITE_PATH}')
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)

USE_TZ = True

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

STATICFILES_DIRS = [
    os.path.join(PROJECT_DIR, 'static'),
]

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Wagtail settings

WAGTAIL_SITE_NAME = "freeturn"

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = env.str("BASE_URL", "http://localhost:8000")
CRISPY_TEMPLATE_PACK = 'bootstrap3'
RECAPTCHA_PUBLIC_KEY = env.str("RECAPTCHA_PUBLIC_KEY", None)
RECAPTCHA_PRIVATE_KEY = env.str("RECAPTCHA_PRIVATE_KEY", None)

EMAIL_CONFIG = env.email_url('EMAIL_URL', default='consolemail://')
vars().update(EMAIL_CONFIG)

TAGGIT_CASE_INSENSITIVE = True
TAGGIT_TAGS_FROM_STRING = 'home.utils.tags_splitter'

DEFAULT_DAILY_RATE = 100
DEFAULT_WORKING_DAYS = 22 * 9
VAT_RATE = Decimal('0.19')
INCOME_TAX_RATE = Decimal('0.41')

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)
SOCIAL_AUTH_URL_NAMESPACE = 'social'

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env.str("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", None)
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env.str("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET", None)

SOCIAL_AUTH_LOGIN_URL = "/admin/account/"
LOGIN_REDIRECT_URL = SOCIAL_AUTH_LOGIN_URL
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://mail.google.com/'
]

SOCIAL_AUTH_PIPELINE = ("utils.social_for_authed_only",) + DEFAULT_AUTH_PIPELINE
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS = {
    'access_type': 'offline'
}
WKHTMLTOPDF_CMD = '/usr/bin/wkhtmltopdf'
WKHTMLTOPDF_CMD_OPTIONS = {
    'quiet': True,
}
GOOGLE_ANALYTICS_JS_PROPERTY_ID = env.str("GOOGLE_ANALYTICS_ID", default="UA-123456-7")
MAILBOX_LABEL = "CRM"
DEFAULT_VAT = 19

AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME", None)
if AWS_STORAGE_BUCKET_NAME:
    AWS_ACCESS_KEY_ID = env.str("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env.str("AWS_SECRET_ACCESS_KEY")
    AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
    AWS_DEFAULT_ACL = "private"
    AWS_S3_FILE_OVERWRITE = False
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
DJANGO_REDIS_IGNORE_EXCEPTIONS = True
CACHES = {
    'default': env.cache('REDIS_URL', 'locmemcache://')
}
SECURE_PROXY_SSL = env.bool('SECURE_PROXY_SSL', False)
if SECURE_PROXY_SSL:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True

WHITENOISE_STORAGE = env.bool('SECURE_PROXY_SSL', False)
if WHITENOISE_STORAGE:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

WKHTMLTOPDF_CMD = env.str('WKHTMLTOPDF_CMD', default='/usr/bin/wkhtmltopdf')
