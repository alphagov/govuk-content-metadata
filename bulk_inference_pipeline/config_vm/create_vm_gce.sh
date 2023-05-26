#!/bin/bash

# General info
# This script does:
# 1. Create an ubuntu VM on GCE

# 1. Create the VM with GPU with our project's service account access
gcloud compute instances create ${VM_NAME} \
    --machine-type ${MACHINE_TYPE} \
    --zone ${ZONE} \
    --boot-disk-size ${BOOT_DISK_SIZE}GB \
    --accelerator type=${GPU_TYPE},count=${GPU_COUNT} \
    --image-family ubuntu-2004-lts \
    --image-project ubuntu-os-cloud \
    --maintenance-policy TERMINATE \
    --restart-on-failure \
    --service-account=${NER_BULK_INFERENCE_SA} \
    --scopes https://www.googleapis.com/auth/cloud-platform \
    --description "${DESCRIPTION}"

# Wait 15 sec before executing the rest to ensure the VM is up and running before ssh-ing into it
sleep 15
