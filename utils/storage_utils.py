from google.cloud import storage

def delete_image_from_bucket(bucket_name, deal_id, image_filename):
    """Deletes an image from a Google Cloud Storage bucket."""
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f"deals/{deal_id}/{image_filename}")  # Construct the correct path
        blob.delete()
        return True
    except Exception as e:
        print(f"Error deleting image from bucket: {str(e)}")
        return False