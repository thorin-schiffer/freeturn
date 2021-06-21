FROM python:3.9.4
ENV PYTHONUNBUFFERED 1
ENV WKHTMLTOPDF_CMD=/usr/local/bin/wkhtmltopdf
EXPOSE 8000/tcp

RUN apt-get update && apt-get -y install libssl-dev --no-install-recommends
RUN wget https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6-1/wkhtmltox_0.12.6-1.focal_amd64.deb && dpkg -i wkhtmltox_0.12.6-1.focal_amd64.deb ; apt-get install -f -y

RUN pip install --upgrade pip=="20.0.2" && pip install --upgrade pipenv

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --system --deploy --ignore-pipfile --dev

WORKDIR /app
COPY . /app

RUN pytest -n auto

CMD inv unicorn -f -h 0.0.0.0
