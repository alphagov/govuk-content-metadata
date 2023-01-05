#! /bin/bash

# This script does:
# 1. Attach a start-up script to the VM instance
# 2. Create a schedule for the VM
# 3. Attach the schedule to the VM

# Requires the following env variable to be defined:
# STARTUP_SCRIPT_PATH
# VM_NAME
# SCHEDULE_NAME

# Stop the VM
gcloud compute instances stop ${VM_NAME}

# Add start-up script to existing VM instance
gcloud compute instances add-metadata ${VM_NAME} \
  --metadata-from-file startup-script=${STARTUP_SCRIPT_PATH}

# Create schedule
gcloud compute resource-policies create instance-schedule ${SCHEDULE_NAME} \
  --description='Twice on the 1st and 15th of each month, start VMs at 0:10 AM and stop VMs at 9 PM' \
  --region=europe-west2 \
  --vm-start-schedule='10 0 1,15 * *' \
  --vm-stop-schedule='0 21 1,15 * *'

# Add the schedule
gcloud compute instances add-resource-policies ${VM_NAME} \
    --resource-policies=${SCHEDULE_NAME} \
    --zone=europe-west2-a

# Ref: https://cloud.google.com/compute/docs/instances/schedule-instance-start-stop
# UTC time used by default
# if no --end-date specified, this is endless
