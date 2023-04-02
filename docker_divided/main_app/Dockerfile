FROM python:3.10-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir

COPY ./app/ ./app/
COPY ./alembic/ ./alembic/
COPY ./main_app.py .
COPY ./alembic.ini .
