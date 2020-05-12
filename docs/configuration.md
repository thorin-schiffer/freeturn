# Configuration

## Environment variables

Freeturn uses [django-environ](https://github.com/joke2k/django-environ) to configure the application over environment
variables and dotenv files. All the environment variables can be found in `.env_template`, here they are:

```.env
# recaptcha config for the forms
RECAPTCHA_PUBLIC_KEY=
RECAPTCHA_PRIVATE_KEY=
# sentry project id
SENTRY_DSN=
# email url, see django-environ docs for more info
EMAIL_URL=
# oauth2 social auth config for google login
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=
# aws access keys
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
# static and media storage aws s3 bucket name
AWS_STORAGE_BUCKET_NAME=
# aws storage account id and user for s3 policy config, see https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html
AWS_STORAGE_ACCOUNT_ID=
AWS_STORAGE_USER=
# redis url using django-environ notation
REDIS_URL='rediscache://127.0.0.1:6379/1?client_class=django_redis.client.DefaultClient'
# google analytics id
GOOGLE_ANALYTICS_ID=UA-123456-7
# django debug mode, dont' set in prod
DEBUG=True
# django debug toolbar, see https://django-debug-toolbar.readthedocs.io/en/latest/
DEBUG_TOOLBAR=
# secret key for your project, see https://djecrety.ir/
SECRET_KEY=1234567
# use redis to cache templates
CACHE_TEMPLATES=
# set in prod while using https as transport and heroku
SECURE_PROXY_SSL=
# whitenoise storage compresses the media assets, recommended in prod
WHITENOISE_STORAGE=
# path to set wkhtml binary, usually /usr/bin/wkhtmltopdf, for heroku buildback /app/bin/wkhtmltopdf
# use which wkhtmltopdf in the container to make sure it's there
WKHTMLTOPDF_CMD=
# monitoring with scout apm, https://docs.scoutapm.com/#django
SCOUT_MONITOR=
```
Additionally django environ offers (see [docs](https://github.com/joke2k/django-environ#supported-types))
- `DATABASE_URL` for configuring the database, defaults to `./db.sqlite3`
- `REDIS_URL` for configuring redis / cache urls (caches default to [locmemcache](https://docs.djangoproject.com/en/3.0/topics/cache/#local-memory-caching))
- `EMAIL_URL` for configuring email  (defaults to `consolemail`)

Most of the activation different services and features in freeturn, default values are not suitable
for production. Let's dig into it.

## Database

```python
DATABASE_URL = 'sqlite:///<PROJECT_DIR>/db.sqlite3'
```

The default config uses locally stored sqlite database, which is particularly comfortable for local development, because
of it's speed and quick setup. Besides that docker container and heroku dynos don't have persistent storages out of box,
which makes them easily disposable and reproducable.

Long story short, this is not convenient for production use. Heroku dynos offer free postgres add-ons, which inject the
database URL over the env variable `DATABASE_URL`, which makes it plug and play ready. Of course you are free to use any
DBMS of your choice, consult [django-environ](https://github.com/joke2k/django-environ#supported-types) docs for correct
building of database URLs.

## Storage

For same reason as the filesystem based databases are not suitable for production, [the local filesystem storage won't
work for heroku](https://help.heroku.com/K1PPS2WM/why-are-my-file-uploads-missing-deleted). This makes storing the
uploads aka media files over heroku quite a peculiar task. Heroku recommends using AWS S3 for that, here is how it can
be done.

### AWS credentials

```python
AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''
```

AWS credentials are the main key pair for you to access your AWS services. Freeturn utilizes [django-storages](https://django-storages.readthedocs.io/en/latest/)
for accessing the s3 storage and configuring it. Find more information on s3 in particular [here](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html).

### S3 bucket
```python
AWS_STORAGE_BUCKET_NAME=''
```

s3 bucket is an analog of a hard drive in terms of AWS cloud storage. s3 as such mimics the popular filesystems, with
multiple differences though. Freeturn needs to know which bucket in your AWS account to use.

### S3 bucket policy
```python
AWS_STORAGE_ACCOUNT_ID=''
AWS_STORAGE_USER=''
```

Freeturn depends on [wagtail-storages](https://github.com/torchbox/wagtail-storages) for managing the sensitive uploads
securely, which requires some addional configuration steps. You can either copypast the wagtail-storages's or manually create the s3 bucket
policy for your storage, that doesn't require `AWS_STORAGE_ACCOUNT_ID` nor `AWS_STORAGE_USER` to be configured.
What you need those settings for, is that if you want to install the policy from template, which you can find in `s3_policy.json.template`.
This is pretty much the recommended policy from `wagtail-storages`, where the user name and account id are injected as context.
See [the corresponding AWS docs](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html) to know
how you can find out your account id and username.

## Recaptcha

```python
RECAPTCHA_PUBLIC_KEY=''
RECAPTCHA_PRIVATE_KEY=''
```

Wagtail exposes the the forms to the wild internet, which means without any DoS protection. Freeturn uses [django-recaptcha2](https://github.com/kbytesys/django-recaptcha2)
for enabling the google's recaptcha and make the submission process easy and comfortable for the visitors.
In order to enable the recaptcha support, you would need the recaptcha public and private keys. See [the recaptcha docs](https://developers.google.com/recaptcha/intro)
to know where you get the keys.

## Email
```python
EMAIL_URL='consolemail://'
```

Freeturn would notify about different event over the email, in order to configure it, email url must be set. Consult [django-environ](https://github.com/joke2k/django-environ)
docs to learn how those URLs are built and also make sure you to take at least a brief look at [django email backends docs](https://docs.djangoproject.com/en/3.0/topics/email/#email-backends)
to find out the difference.

## Google oauth2
- enabling google account connection
- enabling messaging
TBD: mention auth backends?
## Setting up mail checker
TBD


### TBD
- enabling sentry
- enabling frontend caching (CACHE_TEMPLATES, WHITENOISE_STORAGE)
- enabling google analytics
- enabling scout monitoring
