FROM python:3.9-slim

WORKDIR /app

RUN mkdir /app/data

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY config /app/config

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]