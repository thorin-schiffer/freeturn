# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from social_core.pipeline import DEFAULT_AUTH_PIPELINE
import os
from decimal import Decimal
import environ
env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env()
DEBUG = env('DEBUG')

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(PROJECT_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/


# Application definition

INSTALLED_APPS = [
    'home',
    'crm',
    'turbolinks',
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
    'turbolinks.middleware.TurbolinksMiddleware',
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

ROOT_URLCONF = 'portfolio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_DIR, 'templates'),
        ],
        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'context_processors.menu_items'
            ],
        },
    },
]

WSGI_APPLICATION = 'portfolio.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
SECRET_KEY = env('SECRET_KEY')
DATABASES = {
    'default': env.db(),
    'extra': env.db('SQLITE_URL', default='sqlite://./db.sqlite3')
}
# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'),)

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

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

WAGTAIL_SITE_NAME = "portfolio"

# Base URL to use when referring to full URLs within the Wagtail admin backend -
# e.g. in notification emails. Don't include '/admin' or a trailing slash
BASE_URL = 'https://cheparev.com'
CRISPY_TEMPLATE_PACK = 'bootstrap3'
RECAPTCHA_PUBLIC_KEY = env.str("RECAPTCHA_PUBLIC_KEY", None)
RECAPTCHA_PRIVATE_KEY = env.str("RECAPTCHA_PRIVATE_KEY", None)

EMAIL_CONFIG = env.email_url('EMAIL_URL', default='memorymail://')
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

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = env.str("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = env.str("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET")

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
