# GetLinked Mistral-7B-Instruct-v0.1 Deployment Guide on GKE with Google Cloud Endpoint and ESP

This guide outlines the steps for deploying the Mistral-7B-Instruct-v0.1 Large Language Model (LLM) on Google Kubernetes Engine (GKE) with authorization using Google Cloud Endpoint and Extensible Service Proxy (ESP).

## Create Cluster

1. **Creating Kubernetes Cluster**:
   Execute the following command to create a Kubernetes cluster:
   ```bash
   gcloud container clusters create ${CLUSTER_NAME} --location ${REGION} \
     --enable-image-streaming \
     --node-locations=${REGION}-a \
     --workload-pool=${PROJECT_ID}.svc.id.goog \
     --addons GcsFuseCsiDriver \
     --machine-type n2d-standard-4 \
     --num-nodes 1 --min-nodes 1 --max-nodes 5 \
     --ephemeral-storage-local-ssd=count=1 \
     --scopes=https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly \
     --service-account=${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com 
   ```

## Configuring Endpoints

1. **Deploy Endpoints Configuration**:
   Deploy the configuration for the endpoints:
   ```bash
   gcloud endpoints services deploy deploy/getlinked_tgi.yaml
   ```

2. **Check Required Services**:
   Ensure the following Google services are enabled:
   - servicemanagement.googleapis.com (Service Management API)
   - servicecontrol.googleapis.com (Service Control API)
   - endpoints.googleapis.com (Google Cloud Endpoints)

   Confirm the services are enabled:
   ```bash
   gcloud services list
   ```

   If not, enable them:
   ```bash
   gcloud services enable servicemanagement.googleapis.com
   gcloud services enable servicecontrol.googleapis.com
   gcloud services enable endpoints.googleapis.com
   ```

   Also, enable the service endpoint:
   ```bash
   gcloud services enable getlinked-api.endpoints.${PROJECT_ID}.cloud.goog
   ```

## Deploying the API Backend

1. **Create Service Account with Limited Permissions**:
   Execute the following to create a service account and grant necessary permissions:
   ```bash
   # Create service account
   gcloud iam service-accounts create ${SERVICE_ACCOUNT} \
     --display-name="Display Name"

   # Grant permissions
   # Repeat for each role listed below
   gcloud projects add-iam-policy-binding PROJECT_ID \
     --member "serviceAccount:${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com " \
     --role ROLE
   ```
   Replace `ROLE` with each of the following roles:
   - roles/logging.logWriter
   - roles/monitoring.metricWriter
   - roles/monitoring.viewer
   - roles/stackdriver.resourceMetadata.writer
   - roles/autoscaling.metricsWriter
   - roles/container.admin
   - roles/iam.serviceAccountAdmin
   - roles/servicemanagement.serviceController
   - roles/cloudtrace.agent

2. **Create Node Pools with New Service Account**:
   - With GPU:
     ```bash
     gcloud container node-pools create getlinked-g2-standard-16 --cluster ${CLUSTER_NAME} \
       --accelerator type=nvidia-l4,count=1,gpu-driver-version=latest \
       --machine-type g2-standard-16 \
       --ephemeral-storage-local-ssd=count=1 \
       --enable-autoscaling --enable-image-streaming \
       --num-nodes=0 --min-nodes=0 --max-nodes=3 \
       --node-locations ${REGION}-a,${REGION}-c --region ${REGION} \
       --service-account=${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
       --workload-metadata=GKE_METADATA
     ```
   - Without GPU:
     ```bash
     gcloud container node-pools create getlinked-n1-standard-1 --cluster ${CLUSTER_NAME} \
       --machine-type n1-standard-1 \
       --ephemeral-storage-local-ssd=count=1 \
       --enable-autoscaling --enable-image-streaming \
       --num-nodes=0 --min-nodes=0 --max-nodes=3 \
       --node-locations ${REGION}-a,${REGION}-c --region ${REGION} \
       --service-account=${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
       --workload-metadata=GKE_METADATA
     ```

### Enable Workload Identity

1. **Update Existing Cluster**:
   ```bash
   gcloud container clusters update CLUSTER_NAME \
       --region=COMPUTE_REGION \
       --workload-pool=PROJECT_ID.svc.id.goog
   ```

2. **Update Existing Node Pool**:
   ```bash
   gcloud container node-pools update NODEPOOL_NAME \


       --cluster=CLUSTER_NAME \
       --region=COMPUTE_REGION \
       --workload-metadata=GKE_METADATA
   ```

3. **Get Cluster Credentials**:
   ```bash
   gcloud container clusters get-credentials ${CLUSTER_NAME} \
       --region=${REGION}
   ```

4. **Create Namespace for Kubernetes Service Account**:
   ```bash
   kubectl create namespace ${NAMESPACE}
   ```

5. **Create Kubernetes Service Account**:
   ```bash
   kubectl create serviceaccount ${KUBERNETES_SA} \
       --namespace ${NAMESPACE}
   ```

6. **Add IAM Policy Binding**:
   ```bash
   gcloud iam service-accounts add-iam-policy-binding ${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com \
       --role roles/iam.workloadIdentityUser \
       --member "serviceAccount:${PROJECT_ID}.svc.id.goog[${NAMESPACE}/${KUBERNETES_SA}]"
   ```

7. **Annotate Kubernetes Service Account**:
   ```bash
   kubectl annotate serviceaccount ${KUBERNETES_SA} \
       --namespace ${NAMESPACE} \
       iam.gke.io/gcp-service-account=${SERVICE_ACCOUNT}@${PROJECT_ID}.iam.gserviceaccount.com
   ```

8. **Update Pod Spec for Workload Identity**:
   In your deployment YAML, add the following:
   ```yaml
   spec:
     serviceAccountName: KSA_NAME
     nodeSelector:
       iam.gke.io/gke-metadata-server-enabled: "true"
   ```

9. **Add ESP Container and Endpoint to Deployment YAML**:
   ```yaml
   - name: esp
     image: gcr.io/endpoints-release/endpoints-runtime:1
     args: [
       "--http_port=8081",
       "--backend=127.0.0.1:8080",
       "--service=SERVICE_NAME",
       "--rollout_strategy=managed",
     ]
   ```

10. **Apply Updated Configuration**:
    ```bash
    kubectl apply -f DEPLOYMENT_FILE
    ```

11. **Create an API Key**.

12. **Enable DNS**:
    Convert the API endpoint service name to a fully qualified domain name (FQDN).

13. **Test Your Deployment**:
    ```bash
    curl "http://getlinked-api.endpoints.${PROJECT_ID}.cloud.goog:80/generate" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "X-API-KEY: YOUR_API_KEY" \
        -d '{"inputs":"What is Deep Learning?","parameters":{"max_new_tokens":20}}'
    ```

---

Ensure to replace placeholders like `YOUR_PROJECT_ID`, `SA_NAME`, `PROJECT_ID`, `ROLE`, `CLUSTER_NAME`, `COMPUTE_REGION`, `NODEPOOL_NAME`, `KSA_NAME`, `SERVICE_NAME`, `DEPLOYMENT_FILE`, and `YOUR_API_KEY` with actual values relevant to your project.