#! /bin/bash

# This script does:
# 1. Create a schedule for the VM
# 2. Attach the schedule to the VM

# Requires the following env variable to be defined:
# STARTUP_SCRIPT_PATH
# VM_NAME
# SCHEDULE_NAME

# Ref: https://cloud.google.com/compute/docs/instances/schedule-instance-start-stop
# UTC time used by default
# if no --end-date specified, this is endless

# Create schedule
gcloud compute resource-policies create instance-schedule ${SCHEDULE_NAME} \
  --description="${SCHEDULE_DESCRIPTION}" \
  --region=europe-west2 \
  --vm-start-schedule="${SCHEDULE_START_AT}" \
  --vm-stop-schedule="${SCHEDULE_STOP_AT}"

# Add the schedule
gcloud compute instances add-resource-policies ${VM_NAME} \
    --resource-policies=${SCHEDULE_NAME} \
    --zone=europe-west2-a
