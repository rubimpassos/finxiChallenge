FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1

RUN apk update \
  # psycopg2 dependencies
  && apk add --virtual build-deps bash gcc python3-dev musl-dev \
  && apk add postgresql-dev \
  # Compiler for build some wheel files
  && apk add g++ \
  # CFFI dependencies
  && apk add libffi-dev py-cffi

COPY ./docker-entrypoint.sh /docker-entrypoint.sh
RUN sed -i 's/\r//' /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Requirements are installed here to ensure they will be cached.
COPY ./requirements-dev.txt /requirements-dev.txt
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements-dev.txt

WORKDIR /app
