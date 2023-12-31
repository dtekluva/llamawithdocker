## Create Cluster
1. Create the Kubernetes cluster using the following command
```
gcloud container clusters create getlinked-llm --location us-central1 \
  --enable-image-streaming \
  --node-locations=us-central1-a \
  --workload-pool=plasma-shift-409609.svc.id.goog \
  --addons GcsFuseCsiDriver \
  --machine-type n2d-standard-4 \
  --num-nodes 1 --min-nodes 1 --max-nodes 5 \
  --ephemeral-storage-local-ssd=count=1 \
  --scopes=https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly \
  --service-account=gke-sa@plasma-shift-409609.iam.gserviceaccount.com 
```
## Configuring Endpoints
1. Deploy the Endpoints Configuration
```
gcloud endpoints services deploy openapi.yaml
```

2. Checking required services
At a minimum, Endpoints and ESP require the following Google services to be enabled:

servicemanagement.googleapis.com: Service Management API
servicecontrol.googleapis.com: Service Control API
endpoints.googleapis.com: Google Cloud Endpoints

Run the following command to confirm whether they are enabled
```
gcloud services list
```

If they are not enabled, run 
```
gcloud services enable servicemanagement.googleapis.com
gcloud services enable servicecontrol.googleapis.com
gcloud services enable endpoints.googleapis.com
```

also enable the service endpoint

```
gcloud services enable echo-api.endpoints.YOUR_PROJECT_ID.cloud.goog
```

## Deploying the API backend

1. Create a service account with limited permissions
Run the following commands to create a service account and grant the necessary permissions
```
gcloud iam service-accounts create SA_NAME \
  --display-name="DISPLAY_NAME"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member "serviceAccount:SA_NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/logging.logWriter

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member "serviceAccount:SA_NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/monitoring.metricWriter

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member "serviceAccount:SA_NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/monitoring.viewer

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member "serviceAccount:SA_NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/stackdriver.resourceMetadata.writer

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member "serviceAccount:SA_NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/autoscaling.metricsWriter

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member "serviceAccount:SA_NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/container.admin

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member "serviceAccount:SA_NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role roles/iam.serviceAccountAdmin

gcloud endpoints services add-iam-policy-binding getlinked-api.endpoints.plasma-shift-409609.cloud.goog	 \
  --member serviceAccount:gke-sa@plasma-shift-409609.iam.gserviceaccount.com \
  --role roles/servicemanagement.serviceController

gcloud projects add-iam-policy-binding plasma-shift-409609 \
  --member serviceAccount:gke-sa@plasma-shift-409609.iam.gserviceaccount.com \
  --role roles/cloudtrace.agent
```

2. Create a node pool that uses the new service account
With GPU:
gcloud container node-pools create getlinked-g2-standard-16 --cluster getlinked-llm \
  --accelerator type=nvidia-l4,count=1,gpu-driver-version=latest \
  --machine-type g2-standard-16 \
  --ephemeral-storage-local-ssd=count=1 \
  --enable-autoscaling --enable-image-streaming \
  --num-nodes=0 --min-nodes=0 --max-nodes=3 \
  --node-locations ${REGION}-a,${REGION}-c --region ${REGION} \
  --service-account=gke-sa@plasma-shift-409609.iam.gserviceaccount.com \
  --workload-metadata=GKE_METADATA
```
Without GPU:
gcloud container node-pools create getlinked-n1-standard-1 --cluster getlinked-llm \
  --machine-type n1-standard-1 \
  --ephemeral-storage-local-ssd=count=1 \
  --enable-autoscaling --enable-image-streaming \
  --num-nodes=0 --min-nodes=0 --max-nodes=3 \
  --node-locations us-central1-a,us-central1-c --region us-central1 \
  --service-account=gke-sa@plasma-shift-409609.iam.gserviceaccount.com \
  --workload-metadata=GKE_METADATA
```

### Enable Workload Identity
1. Update an existing cluster
```
gcloud container clusters update CLUSTER_NAME \
    --region=COMPUTE_REGION \
    --workload-pool=PROJECT_ID.svc.id.goog
```

2. Update an existing node pool
```
gcloud container node-pools update NODEPOOL_NAME \
    --cluster=CLUSTER_NAME \
    --region=COMPUTE_REGION \
    --workload-metadata=GKE_METADATA
```

3. Get credentials for your cluster
```
gcloud container clusters get-credentials getlinked-llm \
    --region=us-central1
```

4. Create a namespace to use for the Kubernetes service account.
```
kubectl create namespace getlinked
```

5. Create a Kubernetes service account for your application to use
```
kubectl create serviceaccount getlinked-ksa \
    --namespace getlinked
```

6. Allow the Kubernetes service account to impersonate the IAM service account by adding an IAM policy binding between the two service accounts.
```
gcloud iam service-accounts add-iam-policy-binding gke-sa@plasma-shift-409609.iam.gserviceaccount.com \
    --role roles/iam.workloadIdentityUser \
    --member "serviceAccount:plasma-shift-409609.svc.id.goog[getlinked/getlinked-ksa]"
```

7. Annotate the Kubernetes service account with the email address of the IAM service account
```
kubectl annotate serviceaccount getlinked-ksa \
    --namespace getlinked \
    iam.gke.io/gcp-service-account=gke-sa@plasma-shift-409609.iam.gserviceaccount.com
```

8. Update your Pod spec to schedule the workloads on nodes that use Workload Identity and to use the annotated Kubernetes service account.
```
spec:
  serviceAccountName: KSA_NAME
  nodeSelector:
    iam.gke.io/gke-metadata-server-enabled: "true"
```
also add the namespace to metadata
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: getlinked-mistral-7b
  namespace: NAMESPACE
```

```
apiVersion: v1
kind: Service
metadata:
  name: getlinked-mistral-7b-service
  namespace: NAMESPACE
```
9. Add ESP container and Endpoint to deployment.yaml
```
- name: esp
  image: gcr.io/endpoints-release/endpoints-runtime:1
  args: [
    "--http_port=8081",
    "--backend=127.0.0.1:8080",
    "--service=SERVICE_NAME",
    "--rollout_strategy=managed",
  ]
```
10. Apply the updated configuration to your cluster:
```
kubectl apply -f DEPLOYMENT_FILE
```

10. Create an API key

11. Enable DNS
This converts the API endpoint service name to a fully qualified domain name (FQDN).

12. Test your deployment
```
curl "http://getlinked-api.endpoints.plasma-shift-409609.cloud.goog:80/generate" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-API-KEY: AIzaSyCOqY-4tM4zcGJR71ivPX60tO54OCcSHXU" \
    -d '{"inputs":"What is Deep Learning?","parameters":{"max_new_tokens":20}}'

```