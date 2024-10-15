FROM python:3.9-slim

WORKDIR /app

RUN mkdir /config

COPY config/application_default_credentials.json config/application_default_credentials.json

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV MYSQLCLIENT_CFLAGS="-I/usr/include/mysql"
ENV MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmysqlclient"

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

# Make sure entrypoint.sh is executable
RUN chmod +x /app/entrypoint.sh

# Use entrypoint.sh to run your application
ENTRYPOINT ["/app/entrypoint.sh"]