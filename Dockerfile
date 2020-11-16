
FROM python:3.8.6-slim-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP web/app.py

RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY wsgi.py /app/
COPY manage.py /app/
COPY collect.py /app/
COPY songlen /app/songlen
COPY web /app/web

CMD gunicorn --bind 0.0.0.0:$PORT wsgi
