#public bucket working 

from google.cloud import storage

def create_bucket(bucket_name):
    """Creates a new GCS bucket"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    new_bucket = storage_client.create_bucket(bucket, location="us")
    print(f"Bucket {bucket.name} created.")
    return new_bucket

def upload_file(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

def make_blob_public(bucket_name, blob_name):
    """Makes a blob publicly accessible"""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.make_public()

    print(f"Blob {blob_name} is publicly accessible at {blob.public_url}")
    return blob.public_url

# === MAIN ===
# bucket_name = "your-unique-bucket-name-123"   # must be globally unique
bucket_name = "deepanshu-storage-bucket-457115-v2"
source_file = "index.html"
destination_blob = "index.html"

# Create the bucket
create_bucket(bucket_name)

# Upload the file
upload_file(bucket_name, source_file, destination_blob)

# Make it public and print the URL
url = make_blob_public(bucket_name, destination_blob)
print("Access your file at:", url)
