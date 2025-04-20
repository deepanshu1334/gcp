import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import subprocess
import time

# Set your project ID, VPC, subnet, and region here
PROJECT_ID = 'manifest-zephyr-457115-v2'  # Your Google Cloud project ID
REGION = 'us-central1'  # The region where your VPC and subnet reside
ZONE = 'us-central1-a'  # The zone for the VM (make sure it's within 'us-central1')
INSTANCE_NAME = 'private-ubuntu-vm'  # Name of the VM (for reference)
VPC_NAME = 'hu-devops-25'  # Your VPC network name
SUBNET_NAME = 'private-subnet'  # Your private subnet name
CONNECTOR_NAME = 'my-vpc-connector'  # The name for the VPC connector
APP_ENGINE_ENV = 'flex'  # The App Engine flexible environment

# Authenticate and create the vpcaccess client
def create_vpc_connector():
    # Initialize the VPC Access API client
    credentials, project = google.auth.default()
    vpcaccess = build('vpcaccess', 'v1', credentials=credentials)

    try:
        # Create the VPC Access Connector
        print(f"Creating VPC Access Connector '{CONNECTOR_NAME}'...")

        connector_config = {
            'name': f"projects/{PROJECT_ID}/locations/{REGION}/connectors/{CONNECTOR_NAME}",
            'network': f'projects/{PROJECT_ID}/global/networks/{VPC_NAME}',
            'subnet': f'projects/{PROJECT_ID}/regions/{REGION}/subnetworks/{SUBNET_NAME}',  # Full path for subnet
        }

        operation = vpcaccess.projects().locations().connectors().create(
            parent=f"projects/{PROJECT_ID}/locations/{REGION}",
            body=connector_config
        ).execute()

        # Wait for the operation to complete
        wait_for_operation(vpcaccess, operation)

        print(f"VPC Access Connector '{CONNECTOR_NAME}' created successfully.")
    except HttpError as err:
        print(f"An error occurred: {err}")
        return


def wait_for_operation(vpcaccess, operation):
    """Wait for the operation to complete."""
    print("Waiting for operation to complete...")
    while True:
        result = vpcaccess.projects().locations().operations().get(
            name=operation['name']
        ).execute()

        if result['done']:
            if 'error' in result:
                raise Exception(f"Error: {result['error']}")
            else:
                print("Operation completed successfully.")
                break
        else:
            print("Operation is still in progress...")
        time.sleep(10)


def deploy_app_engine():
    """Deploy the app to App Engine."""
    try:
        print("Deploying the application to App Engine...")
        # Deploy the app using `gcloud app deploy`
        subprocess.run(['gcloud', 'app', 'deploy'], check=True)
        print("App Engine deployment completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Deployment failed: {e}")


if __name__ == "__main__":
    # Step 1: Create the VPC Access Connector
    create_vpc_connector()

    # Step 2: Deploy the app to App Engine
    deploy_app_engine()
