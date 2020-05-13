

<h1 align="center">
    <img width="512" valign="middle" src="https://cheparev-portfolio.s3.amazonaws.com/images/freeturn.original.png" alt="Freeturn">
</h1>

[![eviltnan](https://circleci.com/gh/eviltnan/freeturn.svg?style=shield)](https://app.circleci.com/pipelines/github/eviltnan/freeturn)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![BrowserStack Status](https://automate.browserstack.com/badge.svg?badge_key=OW9FSlpEWUdYb2htbFJYTjRPbEtUVmlNRUhZM2RCNVUwejZ5MzAxUTJLMD0tLUcySUFHVGJVMDdVNzZxZ3VGSTdhSEE9PQ==--2fb0726c5380e49390677a7fdb8e19a5903d2828)](https://automate.browserstack.com/public-build/OW9FSlpEWUdYb2htbFJYTjRPbEtUVmlNRUhZM2RCNVUwejZ5MzAxUTJLMD0tLUcySUFHVGJVMDdVNzZxZ3VGSTdhSEE9PQ==--2fb0726c5380e49390677a7fdb8e19a5903d2828)
[![Maintainability](https://api.codeclimate.com/v1/badges/4aa9a9a8ce0e799208d4/maintainability)](https://codeclimate.com/github/eviltnan/freeturn/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/4aa9a9a8ce0e799208d4/test_coverage)](https://codeclimate.com/github/eviltnan/freeturn/test_coverage)
[![Documentation Status](https://readthedocs.org/projects/freeturn/badge/?version=latest)](https://freeturn.readthedocs.io/en/latest/?badge=latest)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/eviltnan/freeturn/tree/develop)

Freeturn is an open source portfolio and CRM for individual freelance developers.
Based on Django and Wagtail.

😊 Please star and fork if you want to say thank you or just help the project, arigato! 😊

![CRM area](https://cheparev-portfolio.s3.amazonaws.com/images/Office_-_Projects_070.original.png)
![Front page](https://cheparev-portfolio.s3.amazonaws.com/images/Selection_069.original.png)

#### Features

Portfolio:

* minimalistic front page including picture and online identity
* portfolio project pages with all necessary info
* contact form

CRM:

* tracking project leads and budgeting
* clients database
* quick per project CV generation using your project portfolio proven working against HR managers
* Gmail integration, parsing the project description for quick project lead and CV generation
* invoice generation

**WARNING Heroku doesn't provide persistent storage on the [free plan](https://help.heroku.com/K1PPS2WM/why-are-my-file-uploads-missing-deleted),
use s3 or other storage for it**

**Heroku deployments fixtured with superuser admin:admin**
#### Getting started

Freeturn uses Python3. Clone this repository.

##### Setting up python env

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

```
Python 3.7.5 (default, Jan 30 2020, 12:57:36)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.11.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import wagtail
```

##### Setting up binaries

Linux is recommended platform for development, on other systems use Docker to avoid pains.

##### Local development with linux

* copy dotenv template to dotenv: `cp .env_template .env`
* Install wkhtmltopdf: https://wkhtmltopdf.org/, version 0.12.4
* Install wagtail deps: https://docs.wagtail.io/en/v2.7.1/getting_started/index.html#dependencies-needed-for-installation
* Install postgres database: https://www.postgresql.org/
* Install redis key-value storage for caching: https://redis.io/

##### Docker

Dockerfile is for running tests and demonstration purposes only, as heroku is currently considered as the main deployment platform.
Sqlite DB is used, which is not mounted to the outside of the container, so your changes will be gone after you stop the container.
Please submit an issue or a PR with your proposals for the Docker support.
Bind the port 8000 (`-p 8000:8000`)

##### Updating existing installation

The default task for inv is `bootstrap`, use `invoke` to utilize local bootstrapping for development. This would recreate
all the objects created automatically as fixtures.


##### CLI and invoke tasks

CLI tasks are wrapped up with [pyinvoke](https://github.com/pyinvoke/invoke). Invoke is a former fabric1 CLI part now existing as
a separate project. This is preferred over django management commands as the one subjectively requiring less boilerplate.
Please read the docs for pyinvoke for the basics. Available commands can be listed with `inv -l` (`inv` is a shortcut to `invoke`).


##### Setting up s3 for uploads

Consult [the official guide by wagtial](https://wagtail.io/blog/amazon-s3-for-media-files/) and docs for [collections](https://docs.wagtail.io/en/v2.8.1/editor_manual/documents_images_snippets/collections.html).
Collections perms are not usually synced with the ACL for s3, so [wagtail-storages](https://github.com/torchbox/wagtail-storages) is keep the in sync.
