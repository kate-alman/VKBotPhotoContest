FROM python:3.10-alpine

RUN apk add --no-cache gcc musl-dev linux-headers


WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt alembic.ini runner.py /code/

RUN pip install --upgrade pip && pip install -r /code/requirements.txt --no-cache-dir