FROM python:3.10-alpine

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt alembic.ini runner.py /code/

RUN pip install --upgrade pip && pip install -r /code/requirements.txt --no-cache-dir

COPY ./app/app_services/sender/  /code/app/sender_app/
COPY ./app/store/ /code/app/sender_app/app/store/
COPY ./app/contest/ /code/app/sender_app/app/contest/
COPY ./app/app_services/pika_queue/ /code/app/sender_app/app/app_services/pika_queue/
COPY ./app/app_services/vk_api/  /code/app/sender_app/app/app_services/vk_api/
COPY ./app/web/config.py /code/app/sender_app/app/web/
COPY ./app/admin/ /code/app/sender_app/app/admin/
COPY ./runner.py /code/app/sender_app/
