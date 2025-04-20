#working 

import os
from google.cloud import storage
from datetime import timedelta
import uuid

# Use service account key
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "deepanshu-storage.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/user121/Downloads/deepanshu-storage.json"


def create_html_file():
    html_content = "<h1>Hello from Deepanshu</h1>"
    file_path = "index.html"
    with open(file_path, "w") as f:
        f.write(html_content)
    print(f"Created local file: {file_path}")
    return file_path

def create_private_bucket(bucket_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    new_bucket = storage_client.create_bucket(bucket, location="US")
    new_bucket.iam_configuration.uniform_bucket_level_access_enabled = True
    new_bucket.patch()

    print(f"Private bucket {bucket.name} created.")
    return new_bucket

def upload_file(bucket, source_file_path, destination_blob_name):
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_path)
    print(f"File {source_file_path} uploaded as {destination_blob_name}.")

def generate_signed_url(bucket_name, blob_name, expiration_minutes=15):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=timedelta(minutes=expiration_minutes),
        method="GET"
    )

    print(f"\nAccess it securely using this signed URL (valid for {expiration_minutes} minutes):\n{url}")
    return url

if __name__ == "__main__":
    bucket_name = f"private-bucket-{uuid.uuid4().hex[:6]}"
    blob_name = "index.html"

    file_path = create_html_file()
    bucket = create_private_bucket(bucket_name)
    upload_file(bucket, file_path, blob_name)
    generate_signed_url(bucket.name, blob_name)
