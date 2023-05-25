#! /bin/bash

# This script does:
# 1. Attach a start-up script to the VM instance

# Requires the following env variable to be defined:
# STARTUP_SCRIPT_PATH
# VM_NAME

# Stop the VM
gcloud compute instances stop ${VM_NAME}

# Add start-up script to existing VM instance
gcloud compute instances add-metadata ${VM_NAME} \
  --metadata-from-file startup-script=${STARTUP_SCRIPT_PATH}
