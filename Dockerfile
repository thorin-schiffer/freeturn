FROM python:3.7.5
ENV PYTHONUNBUFFERED 1
EXPOSE 8000/tcp

RUN apt-get update && apt-get -y install build-essential wkhtmltopdf

RUN pip install --upgrade pip && pip install --upgrade pipenv

COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
RUN pipenv install --system --deploy --ignore-pipfile --dev

WORKDIR /app
COPY . /app

#RUN pytest -n auto

CMD ./start.sh
