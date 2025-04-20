#working accessing nginx succesfully at public instance 
import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

# Configuration
PROJECT_ID = 'manifest-zephyr-457115-v2'
ZONE = 'us-central1-a'
INSTANCE_NAME = 'public-ubuntu-vm'
IMAGE_PROJECT = 'ubuntu-os-cloud'
IMAGE_FAMILY = 'ubuntu-2004-lts'

def create_instance():
    credentials, project = google.auth.default()
    compute = build('compute', 'v1', credentials=credentials)

    machine_type = f"zones/{ZONE}/machineTypes/n1-standard-1"
    source_disk_image = f"projects/{IMAGE_PROJECT}/global/images/family/{IMAGE_FAMILY}"

    # Startup script to install NGINX
    startup_script = """#!/bin/bash
    sudo apt-get update
    sudo apt-get install -y nginx
    sudo systemctl enable nginx
    sudo systemctl start nginx
    """

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
            'accessConfigs': [{
                'type': 'ONE_TO_ONE_NAT',
                'name': 'External NAT'
            }]
        }],
        'tags': {
            'items': ['http-server']
        },
        'metadata': {
            'items': [{
                'key': 'startup-script',
                'value': startup_script
            }]
        }
    }

    try:
        print(f"Creating public VM instance {INSTANCE_NAME}...")
        operation = compute.instances().insert(
            project=PROJECT_ID,
            zone=ZONE,
            body=config
        ).execute()

        wait_for_operation(compute, operation)
        print(f"Public VM instance {INSTANCE_NAME} created and NGINX installed successfully.")

        # Get instance info to print public IP
        result = compute.instances().get(project=PROJECT_ID, zone=ZONE, instance=INSTANCE_NAME).execute()
        public_ip = result['networkInterfaces'][0]['accessConfigs'][0]['natIP']
        print(f"Access NGINX at: http://{public_ip}")
    
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
