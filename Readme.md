

<h1 align="center">
    <img width="512" valign="middle" src="https://cheparev-portfolio.s3.amazonaws.com/images/freeturn.original.png" alt="Freeturn">
</h1>

[![eviltnan](https://circleci.com/gh/eviltnan/freeturn.svg?style=shield)](https://app.circleci.com/pipelines/github/eviltnan/freeturn)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/eviltnan/freeturn/branch/develop/graph/badge.svg)](https://codecov.io/gh/eviltnan/freeturn)

Freeturn is an open source portfolio and CRM for individual freelance developers.
Based on Django and Wagtail.

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

#### Prerequisites

* Static files on heroku can be only hosted on a persistent file storage, AWS S3 is currently used

#### Installing locally

Freeturn uses Python3. Clone this repository.

##### Setting up python env

* Install for managing your python versions: https://github.com/pyenv/pyenv.
* Update your pyenv versions cache: `pyenv update`
* Install python version 3.7.5 (or other you prefer or one specified in Pipfile): `pyenv install 3.7.5`
* Verify installation with `pyenv versions`. 3.7.5 must be there.
* Configure pyenv using 3.7.5 locally: `pyenv local 3.7.5`. Say `python -V`, it should reply `Python 3.7.5`
* Install pipenv: `pip install pipenv`
* Initialize pipenv environment: `pipenv install --dev`. Dev install dev deps for running tests.
* Enter virtualenv: `pipenv shell`
* Run ipython console: `ipython`. Verify you are in the right env
* Copy dotenv template to .env and fill it up: `cp .env_template .env`
* Install pre-commit hooks with: `pre-commit install`. Read more about pre-commit: https://pre-commit.com/

```python
Python 3.7.5 (default, Jan 30 2020, 12:57:36)
Type 'copyright', 'credits' or 'license' for more information
IPython 7.11.1 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import wagtail
```

##### Setting up binaries

Linux is recommended platform for development, on other systems use Docker to avoid pains.

###### Local development with linux

* copy dotenv template to dotenv: `cp .env_template .env`
* Install wkhtmltopdf: https://wkhtmltopdf.org/, version 0.12.4
* Install wagtail deps: https://docs.wagtail.io/en/v2.7.1/getting_started/index.html#dependencies-needed-for-installation
* Install postgres database: https://www.postgresql.org/
* Install redis key-value storage for caching: https://redis.io/

###### Docker

Dockerfile is for running tests and demonstration purposes only, as heroku is currently considered as the main deployment platform.
Sqlite DB is used, which is not mounted to the outside of the container, so your changes will be gone after you stop the container.
Please submit an issue or a PR with your proposals for the Docker support.
Bind the port 8000 (`-p 8000:8000`)

###### Updating existing installation

The default task for inv is `bootstrap`, use `invoke` to utilize local bootstrapping for development. This would recreate
all the objects created automatically as fixtures.
