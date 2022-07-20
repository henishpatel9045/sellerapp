FROM python:3.10-slim-buster

WORKDIR /app

COPY req.txt req.txt
RUN pip3 install -r req.txt

COPY . .

ENV DJANGO_SUPERUSER_PASSWORD=1234567890

RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
RUN python3 manage.py createsuperuser --noinput --username admin --email admin@django.com

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]