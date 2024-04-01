FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=trading_dashboard.settings


RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /code/
RUN python manage.py collectstatic --no-input