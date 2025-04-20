import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

# Set your project ID and zone here
PROJECT_ID = 'manifest-zephyr-457115-v2'  # Updated project ID
ZONE = 'us-central1-a'  # Or another zone you prefer
INSTANCE_NAME = 'private-ubuntu-vm'
IMAGE_PROJECT = 'ubuntu-os-cloud'
IMAGE_FAMILY = 'ubuntu-2004-lts'  # Ubuntu 20.04 LTS image

# Authenticate and create the compute client
def create_instance():
    # Initialize the Compute Engine client
    credentials, project = google.auth.default()
    compute = build('compute', 'v1', credentials=credentials)

    # Define the machine type and image
    machine_type = f"zones/{ZONE}/machineTypes/n1-standard-1"  # You can change the machine type here
    source_disk_image = f"projects/{IMAGE_PROJECT}/global/images/family/{IMAGE_FAMILY}"

    # Define the configuration for the VM instance
    config = {
        'name': INSTANCE_NAME,
        'machineType': machine_type,
        'disks': [{
            'boot': True,
            'autoDelete': True,
            'initializeParams': {
                'sourceImage': source_disk_image
            }
        }],
        'networkInterfaces': [{
            'network': 'global/networks/default',
            # No accessConfigs means no public IP address
        }],
        'tags': {
            'items': ['http-server', 'https-server']
        },
    }

    try:
        # Create the VM instance
        print(f"Creating private VM instance {INSTANCE_NAME}...")
        operation = compute.instances().insert(
            project=PROJECT_ID,
            zone=ZONE,
            body=config
        ).execute()

        # Wait for the operation to complete
        wait_for_operation(compute, operation)

        print(f"Private VM instance {INSTANCE_NAME} created successfully.")
    
    except HttpError as err:
        print(f"An error occurred: {err}")
        return

def wait_for_operation(compute, operation):
    print("Waiting for operation to complete...")
    while True:
        result = compute.zoneOperations().get(
            project=PROJECT_ID,
            zone=ZONE,
            operation=operation['name']
        ).execute()

        if result['status'] == 'DONE':
            if 'error' in result:
                raise Exception(f"Error: {result['error']}")
            else:
                print("Operation completed successfully.")
                break
        else:
            print("Operation is still in progress...")
        time.sleep(10)

if __name__ == "__main__":
    create_instance()
