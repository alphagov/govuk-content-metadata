export N=1
export VM_NAME=bulk-inference-phase1-ubuntu-gpu-cuda117
export DOCKER_IMAGE_NAME=ner-bulk-inference-phase1
export MACHINE_TYPE=n1-standard-16
export ZONE=europe-west2-a
export BOOT_DISK_SIZE=100
export GPU_TYPE=nvidia-tesla-t4
export GPU_COUNT=1
export DESCRIPTION='govNER bulk inference phase-1 pipeline'
# Google Scheduler
export SCHEDULE_NAME=bulk-inference-phase1-schedule
export SCHEDULE_DESCRIPTION='Once on the 1st of each month, start VMs at 0:10 AM and stop VMs at 22:00 PM'
export SCHEDULE_START_AT='10 0 1 * *'
export SCHEDULE_STOP_AT='0 22 1 * *'
