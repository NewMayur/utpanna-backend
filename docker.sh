# Build the image
sudo docker build -t utpanna-backend .

# Run the container with mounted credentials
sudo docker run -p 8080:8080 --env-file .env -v $(pwd)/config:/config -e GOOGLE_APPLICATION_CREDENTIALS=/config/application_default_credentials.json utpanna-backend