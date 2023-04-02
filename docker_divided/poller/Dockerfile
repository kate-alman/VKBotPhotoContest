FROM python:3.10-alpine

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt alembic.ini runner.py /code/

RUN pip install --upgrade pip && pip install -r /code/requirements.txt --no-cache-dir

COPY ./app/app_services/poller/  /code/app/poller_app/
COPY ./app/app_services/pika_queue/ /code/app/poller_app/app/app_services/pika_queue/
COPY ./app/app_services/vk_api/  /code/app/poller_app/app/app_services/vk_api/
COPY ./app/web/config.py /code/app/poller_app/app/web/
COPY ./app/contest/ /code/app/poller_app/app/contest/
COPY ./app/store/ /code/app/poller_app/app/store/
COPY ./app/admin/ /code/app/poller_app/app/admin/
COPY ./runner.py /code/app/poller_app/
