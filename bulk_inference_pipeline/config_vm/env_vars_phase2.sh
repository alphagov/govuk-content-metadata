export N=2
export VM_NAME=bulk-inference-phase2-ubuntu-gpu-cuda117
export DOCKER_IMAGE_NAME=ner-bulk-inference-phase2
export MACHINE_TYPE=n1-standard-16
export ZONE=europe-west2-a
export BOOT_DISK_SIZE=100
export GPU_TYPE=nvidia-tesla-t4
export GPU_COUNT=1
export DESCRIPTION='govNER bulk inference phase-2 pipeline'
# Google Scheduler
export SCHEDULE_NAME=bulk-inference-phase2-schedule
export SCHEDULE_DESCRIPTION='Once on the 1st of each month, start VMs at 22:30 AM and stop VMs at 20:30 PM the next day'
export SCHEDULE_START_AT='30 22 1 * *'
export SCHEDULE_STOP_AT='30 20 2 * *'
