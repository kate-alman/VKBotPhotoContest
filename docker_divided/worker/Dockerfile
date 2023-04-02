FROM python:3.10-alpine

WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt alembic.ini runner.py /code/

RUN pip install --upgrade pip && pip install -r /code/requirements.txt --no-cache-dir

COPY ./app/app_services/worker/  /code/app/worker/
COPY ./app/store/ /code/app/worker/app/store/
COPY ./app/web/config.py /code/app/worker/app/web/
COPY ./app/contest/ /code/app/worker/app/contest/
COPY ./app/app_services/pika_queue/ /code/app/worker/app/app_services/pika_queue/
COPY ./app/app_services/vk_api/  /code/app/worker/app/app_services/vk_api/
COPY ./app/admin/ /code/app/worker/app/admin/
COPY ./runner.py /code/app/worker/
