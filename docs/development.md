# Development

Freeturn uses Python3.

## Setting up python env

* Install pyenv for managing your python versions: https://github.com/pyenv/pyenv.
* Update your pyenv versions cache: `pyenv update`
* Install python version 3.7.5 (or other you prefer or one specified in Pipfile): `pyenv install 3.7.5`
* Verify installation with `pyenv versions`. 3.7.5 must be there.
* Configure pyenv using 3.7.5 locally: `pyenv local 3.7.5`. Say `python -V`, it should reply `Python 3.7.5`
* Install pipenv: `pip install pipenv`
* Initialize pipenv environment: `pipenv install --dev`. Dev install dev deps for running tests.
* Enter virtualenv: `pipenv shell`
* Run ipython console: `ipython`. Verify you are in the right env
* Copy dotenv template to .env and fill it up: `cp .env_template .env`. See https://github.com/joke2k/django-environ for more information.
Various features can be activated over the environment, see .env_template for annotations and options
* Install pre-commit hooks with: `pre-commit install`. Read more about pre-commit: https://pre-commit.com/

```python
Python 3.7.5 (default, Jan 30 2020, 12:57:36)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.11.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import wagtail
```

## Setting up binaries

Linux is recommended platform for development, on other systems use Docker to avoid pains.

## Local development with linux

* copy dotenv template to dotenv: `cp .env_template .env`
* Install wkhtmltopdf: https://wkhtmltopdf.org/, version 0.12.4
* Install wagtail deps: https://docs.wagtail.io/en/v2.7.1/getting_started/index.html#dependencies-needed-for-installation
* Install postgres database: https://www.postgresql.org/
* Install redis key-value storage for caching: https://redis.io/

## Docker

Dockerfile is for running tests and demonstration purposes only, as heroku is currently considered as the main deployment platform.
Sqlite DB is used, which is not mounted to the outside of the container, so your changes will be gone after you stop the container.
Please submit an issue or a PR with your proposals for the Docker support.
Bind the port 8000 (`-p 8000:8000`)

## Updating existing installation

The default task for inv is `bootstrap`, use `invoke` to utilize local bootstrapping for development. This would recreate
all the objects created automatically as fixtures.


## CLI and invoke tasks

CLI tasks are wrapped up with [pyinvoke](https://github.com/pyinvoke/invoke). Invoke is a former fabric1 CLI part now existing as
a separate project. This is preferred over django management commands as the one subjectively requiring less boilerplate.
Please read the docs for pyinvoke for the basics. Available commands can be listed with `inv -l` (`inv` is a shortcut to `invoke`).


## Setting up s3 for uploads

Consult [the official guide by wagtial](https://wagtail.io/blog/amazon-s3-for-media-files/) and docs for [collections](https://docs.wagtail.io/en/v2.8.1/editor_manual/documents_images_snippets/collections.html).
Collections perms are not usually synced with the ACL for s3, so [wagtail-storages](https://github.com/torchbox/wagtail-storages) is keep the in sync.
