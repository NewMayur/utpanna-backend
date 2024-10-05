FROM python:3.9-slim

WORKDIR /app

RUN mkdir /app/data

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for mysqlclient
ENV MYSQLCLIENT_CFLAGS="-I/usr/include/mysql"
ENV MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu -lmysqlclient"

# Copy requirements first to leverage Docker cache
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application
COPY . .

# Make sure the entrypoint script is executable
RUN chmod +x /app/entrypoint.sh

# Use the entrypoint script to run the application
ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
