from google.cloud import secretmanager
import google.auth
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
import os
import base64

def access_secret_version(project_id, secret_id, version_id=1):
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        print(f"Requesting secret: {name}")
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Error accessing secret: {e}")
        # Check if credentials are set up correctly
        _, project = google.auth.default()
        print(f"Default project: {project}")
        raise

def get_default_credentials():
    credentials, project = google.auth.default()
    return credentials, project



# Function to generate a JWT secret key
def generate_jwt_secret_key():
    password = os.urandom(16)  # Generate a random password
    salt = os.urandom(16)      # Generate a random salt

    # Derive the secret key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key.decode()

# Generate the secret key
# secret_key = generate_jwt_secret_key()
# print(f"Your JWT secret key: {secret_key}")
