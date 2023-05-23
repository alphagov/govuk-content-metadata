#! /bin/bash

# General info
# This script does:
# 1. Create an ubuntu VM on GCE

# 1. Create the VM with GPU with our project's service account access
gcloud compute instances create ${VM_NAME} \
    --machine-type n1-standard-16 \
    --zone europe-west2-a \
    --boot-disk-size 100GB \
    --accelerator type=nvidia-tesla-t4,count=1 \
    --image-family ubuntu-2004-lts \
    --image-project ubuntu-os-cloud \
    --maintenance-policy TERMINATE \
    --restart-on-failure \
    --service-account=${NER_BULK_INFERENCE_SA} \
    --scopes https://www.googleapis.com/auth/cloud-platform \
    --description 'govNER bulk inference pipeline'

# Wait 15 sec before executing the rest to ensure the VM is up and running before ssh-ing into it
sleep 15
