#!/bin/bash

####### ----------------------------------- #######
# This bash script does 3 things:

# 1) Upload the custom model (from custom container) to Vertex AI Model Registry
# 2) Create a Vertex AI endpoint [optional]
# 3) Deploy the model to the endpoint [optional]

# The following command-line options are available:
#  --deploy, -d    to create a Vertex AI endpoinnt and deploy the model to it

# since steps 2) and 3) are only needed for online (real-time) predictions
# but they are good for testing and development so they are included but as optional steps.

# From your terminal, run:
# bash deploy_to_vertexai.sh
# to execute Step 1 only
# bash deploy_to_vertexai.sh --deploy
# to execute Steps 1, 2 and 3.

# NOTE1: Change the value of the enviornment variables in the script if anything needs changes.

# NOTE2:  There seems to be an "issue" with custom model within custom container and Vertex AI
# in that if the image gets updated (new "latest" version), one needs to create a new model and endpoint in Vertex AI every time.
# https://stackoverflow.com/questions/70833206/update-a-custom-container-model-in-vertexai-in-gcp
# So, this is what we do here.

####### ----------------------------------- #######

# General
GCP_PROJECT=cpto-content-metadata
REGION=europe-west2
SERVICE_ACCOUNT_EMAIL=${GCP_NER_MODEL_API_SA}

# Unique name for the model
TIMESTAMP=$(date +%Y%m%d)
MODEL_NAME=ner-trf-combo-model-${TIMESTAMP}
MODEL_DESCRIPTION='GovNER Transformer model served using FastAPI (phase1 and phase2 entities)'
# Model info
DOCKER_IMAGE_URI=europe-west2-docker.pkg.dev/cpto-content-metadata/cpto-content-metadata-docker-repo/fastapi-ner-trf
API_PREDICT_ROUTE=/ner-vertex-ai
API_HEALTH_ROUTE=/health-check

# Name for the endpoint
ENDPOINT_NAME=ner_vertex_endpoint

# Deployment info
MACHINE_TYPE=n1-standard-2
MIN_REPLICA_COUNT=1
MAX_REPLICA_COUNT=4


# Set up logic
# for deployment to endpoint
DEPLOY_FLAG=false
while [ True ]; do
if [ "$1" = "--deploy" -o "$1" = "-d" ]; then
    DEPLOY_FLAG=true
    shift 1
else
    break
fi
done


# 1) Upload model to Vertex AI Model Register
# https://cloud.google.com/sdk/gcloud/reference/ai/models/upload
echo "Upload model to Vertex AI Model Register"

# delete any existing models with this name (if any)
# do nothing if model with this name does not already exist
for MODEL_ID in $(gcloud ai models list --region=$REGION \
        --format='value(MODEL_ID)' --filter=display_name=${MODEL_NAME}); do
    echo "Deleting existing $MODEL_NAME ... $MODEL_ID "
    gcloud ai models delete --region=$REGION $MODEL_ID
done

# upload model
# container-ports (default) is the correct 8080
gcloud ai models upload \
  --region=$REGION \
  --display-name=$MODEL_NAME \
  --container-image-uri=$DOCKER_IMAGE_URI:latest \
  --container-predict-route=$API_PREDICT_ROUTE \
  --container-health-route=$API_HEALTH_ROUTE \
  --description="$MODEL_DESCRIPTION"

# retreive Model ID
MODEL_ID=$(gcloud ai models list --region=$REGION \
    --format='value(MODEL_ID)' \
    --filter=display_name=${MODEL_NAME})
echo "Successfully uploaded MODEL_ID=$MODEL_ID"


# If flag provided...
if "$DEPLOY_FLAG"; then


    # 2) Create endpoint if not already existing
    # https://cloud.google.com/sdk/gcloud/reference/ai/endpoints/create
    # https://cloud.google.com/vertex-ai/docs/predictions/get-predictions#get_online_predictions
    # NOTE: Not needed to deploy model to endpoint for batch predictions but recommended for quick testing and development

    echo "Create endpoint if not already existing"

    if [[ $(gcloud ai endpoints list --region=$REGION \
            --format='value(DISPLAY_NAME)' --filter=display_name=${ENDPOINT_NAME}) ]]; then
        echo "Endpoint $ENDPOINT_NAME for model $MODEL_NAME already exists"
    else
        # create endpoint
        echo "Creating Endpoint $ENDPOINT_NAME for model $MODEL_NAME"
        gcloud ai endpoints create \
            --project=${GCP_PROJECT} \
            --region=${REGION} \
            --display-name=${ENDPOINT_NAME}
    fi

    # retrieve Endpoint ID
    ENDPOINT_ID=$(gcloud ai endpoints list --region=$REGION \
        --format='value(ENDPOINT_ID)' \
        --filter=display_name=${ENDPOINT_NAME})
    echo "ENDPOINT_ID=$ENDPOINT_ID"


    # 4) Deploy your model to the Vertex AI Endpoint.
    # https://cloud.google.com/sdk/gcloud/reference/ai/endpoints/deploy-model
    # the first ID is the id of endpoint created above
    # model captures the ID of the registered model

    echo "Deploy model to the Vertex AI endpoint"

    gcloud ai endpoints deploy-model $ENDPOINT_ID \
    --project=$GCP_PROJECT \
    --region=$REGION \
    --model=$MODEL_ID \
    --display-name=$MODEL_NAME \
    --machine-type=$MACHINE_TYPE \
    --min-replica-count=$MIN_REPLICA_COUNT\
    --max-replica-count=$MAX_REPLICA_COUNT \
    --traffic-split=0=100 \
    --service-account=$SERVICE_ACCOUNT_EMAIL

fi
