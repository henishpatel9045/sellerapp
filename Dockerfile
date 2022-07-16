FROM python:3.10-slim-buster

WORKDIR /app

COPY req.txt req.txt
RUN pip3 install -r req.txt

COPY . .

RUN python3 manage.py makemigrations
RUN python3 manage.py migrate
RUN python3 manage.py createsuperuser

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]