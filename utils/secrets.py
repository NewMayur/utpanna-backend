from google.cloud import secretmanager
import google.auth

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