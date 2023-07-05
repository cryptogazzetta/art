from google.cloud import storage

# Function to store file in GCS
def store_file_in_gcs(bucket_name, local_file_path, gcs_file_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(gcs_file_name)
    blob.upload_from_filename(local_file_path)
    print(f"File stored successfully in GCS: gs://{bucket_name}/{gcs_file_name}")

# Function to retrieve file from GCS
def retrieve_file_from_gcs(bucket_name, gcs_file_name, local_file_path):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(gcs_file_name)
    blob.download_to_filename(local_file_path)
    print(f"File retrieved from GCS: {local_file_path}")

# Function that checks whether file exists on GCS
def file_exists(bucket_name, file_name):
    client = storage.Client()
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    return blob.exists()

