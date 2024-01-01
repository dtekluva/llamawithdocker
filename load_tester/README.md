# GetLinked LLM API Load Tester

## Overview
This guide provides step-by-step instructions for setting up and deploying a load testing environment for the GetLinked LLM API using Locust in a Google Kubernetes Engine (GKE) cluster. 

Follow these steps to build a Docker image for Locust, set up a GKE cluster, and deploy Locust components.

## Prerequisites
- Ensure you have the `gcloud` CLI installed and configured for your project.
- Docker is installed on your machine for building the Locust image.

## Configuration Steps

### 1. Environment Setup
Set up the necessary environment variables for the Google Cloud project ID, region, and zone.

```bash
PROJECT=$(gcloud config get-value project)
REGION="us-central1"
ZONE="us-central1-a"
CLUSTER="getlinked-load-test"
TARGET="$EXTERNAL_IP"

# Set your compute region and zone
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE
```

### 2. Build the Locust Docker Image
Create a Docker image for the Locust load tester and push it to Google Container Registry.

```bash
gcloud builds submit --tag gcr.io/$PROJECT/getlinked-locust-tester:latest docker/.
```

### 3. Create GKE Cluster
Deploy a Google Kubernetes Engine cluster with the specified number of nodes.

```bash
gcloud container clusters create $CLUSTER \
  --zone $ZONE \
  --num-nodes=5 \
  --machine-type=e2-medium \
  --disk-type=pd-standard \
  --disk-size=10
```

### 4. Deploy Locust Master
Apply the Kubernetes configuration to deploy the Locust master.

```bash
kubectl apply -f getlinked-locust-master-controller.yaml
```

### 5. Set Up Locust Master Service
Deploy the Locust master service for external access.

```bash
kubectl apply -f getlinked-locust-master-service.yaml
```

### 6. Retrieve External IP
Get the external IP address of the Locust master service.

```bash
kubectl get svc locust-master
```

### 7. Deploy Locust Workers
Deploy the Locust worker controllers for distributed load testing.

```bash
kubectl apply -f getlinked-locust-worker-controller.yaml
```

### 8. Access the Locust Web Interface
Open a web browser and navigate to the Locust web UI using the external IP.

```
http://$EXTERNAL_IP:8089
```

### 9. Begin Load Testing
Initiate the load test by entering the desired number of users and spawn rate on the Locust UI.

- Number of users: `200`
- Spawn rate: `10 users per second`

## Conclusion
By following these steps, you will successfully deploy a scalable load testing environment for the GetLinked LLM API using Locust on a GKE cluster. Monitor the performance and adjust parameters as needed to simulate different load scenarios.