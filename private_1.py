#private vm with vpc and subnet 

# import os
# import google.auth
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError
# import time

# # Set your project ID, VPC, subnet, and zone here
# PROJECT_ID = 'manifest-zephyr-457115-v2'  # Your Google Cloud project ID
# ZONE = 'us-central1-a'  # The zone for the VM (make sure it's within 'us-central1')
# INSTANCE_NAME = 'private-ubuntu-vm-2'  # New name for the VM to avoid conflict
# IMAGE_PROJECT = 'ubuntu-os-cloud'  # The project where the Ubuntu image resides
# IMAGE_FAMILY = 'ubuntu-2004-lts'  # The image family (Ubuntu 20.04 LTS)
# VPC_NAME = 'hu-devops-25'  # Your VPC network name
# SUBNET_NAME = 'private-subnet'  # Your private subnet name

# # Authenticate and create the compute client
# def create_instance():
#     # Initialize the Compute Engine client
#     credentials, project = google.auth.default()
#     compute = build('compute', 'v1', credentials=credentials)

#     # Define the machine type and image
#     machine_type = f"zones/{ZONE}/machineTypes/n1-standard-1"  # You can change the machine type here
#     source_disk_image = f"projects/{IMAGE_PROJECT}/global/images/family/{IMAGE_FAMILY}"

#     # Define the network and subnet configuration
#     network_interface = {
#         'network': f'global/networks/{VPC_NAME}',  # Specify the VPC network
#         'subnetwork': f'regions/us-central1/subnetworks/{SUBNET_NAME}',  # Specify the correct region 'us-central1' and subnet
#         # No accessConfigs means no public IP address (this creates a private VM)
#     }

#     # Define the configuration for the VM instance
#     config = {
#         'name': INSTANCE_NAME,
#         'machineType': machine_type,
#         'disks': [{
#             'boot': True,
#             'autoDelete': True,
#             'initializeParams': {
#                 'sourceImage': source_disk_image
#             }
#         }],
#         'networkInterfaces': [network_interface],  # Attach the VM to the private network
#         'tags': {
#             'items': ['http-server', 'https-server']  # Tags for access control (e.g., firewall rules)
#         },
#     }

#     try:
#         # Create the VM instance
#         print(f"Creating private VM instance {INSTANCE_NAME}...")
#         operation = compute.instances().insert(
#             project=PROJECT_ID,
#             zone=ZONE,
#             body=config
#         ).execute()

#         # Wait for the operation to complete
#         wait_for_operation(compute, operation)

#         print(f"Private VM instance {INSTANCE_NAME} created successfully.")
    
#     except HttpError as err:
#         print(f"An error occurred: {err}")
#         return

# def wait_for_operation(compute, operation):
#     print("Waiting for operation to complete...")
#     while True:
#         result = compute.zoneOperations().get(
#             project=PROJECT_ID,
#             zone=ZONE,
#             operation=operation['name']
#         ).execute()

#         if result['status'] == 'DONE':
#             if 'error' in result:
#                 raise Exception(f"Error: {result['error']}")
#             else:
#                 print("Operation completed successfully.")
#                 break
#         else:
#             print("Operation is still in progress...")
#         time.sleep(10)

# if __name__ == "__main__":
#     create_instance()




## private VM with nginx and ssh into it 

import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import time

# Configuration
PROJECT_ID = 'manifest-zephyr-457115-v2'
ZONE = 'us-central1-a'
INSTANCE_NAME = 'private-ubuntu-vm-2'
IMAGE_PROJECT = 'ubuntu-os-cloud'
IMAGE_FAMILY = 'ubuntu-2004-lts'
VPC_NAME = 'hu-devops-25'
SUBNET_NAME = 'private-subnet'

def create_instance():
    credentials, project = google.auth.default()
    compute = build('compute', 'v1', credentials=credentials)

    machine_type = f"zones/{ZONE}/machineTypes/n1-standard-1"
    source_disk_image = f"projects/{IMAGE_PROJECT}/global/images/family/{IMAGE_FAMILY}"

    startup_script = """#!/bin/bash
    apt-get update
    apt-get install -y nginx
    systemctl enable nginx
    systemctl start nginx
    """

    network_interface = {
        'network': f'global/networks/{VPC_NAME}',
        'subnetwork': f'regions/us-central1/subnetworks/{SUBNET_NAME}',
    }

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
        'networkInterfaces': [network_interface],
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
        print(f"Creating private VM instance {INSTANCE_NAME}...")
        operation = compute.instances().insert(
            project=PROJECT_ID,
            zone=ZONE,
            body=config
        ).execute()

        wait_for_operation(compute, operation)

        print(f"✅ Private VM '{INSTANCE_NAME}' with NGINX created successfully.")
    
    except HttpError as err:
        print(f"❌ An error occurred: {err}")

def wait_for_operation(compute, operation):
    print("⏳ Waiting for operation to complete...")
    while True:
        result = compute.zoneOperations().get(
            project=PROJECT_ID,
            zone=ZONE,
            operation=operation['name']
        ).execute()

        if result['status'] == 'DONE':
            if 'error' in result:
                raise Exception(f"❌ Error: {result['error']}")
            print("✅ Operation completed successfully.")
            break
        time.sleep(5)

if __name__ == "__main__":
    create_instance()
