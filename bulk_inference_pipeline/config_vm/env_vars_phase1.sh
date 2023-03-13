VM_NAME=bulk-inference-phase1-ubuntu-gpu
DOCKER_IMAGE_NAME=ner-bulk-inference-phase1
STARTUP_SCRIPT_PATH=config_vm/startup_script_vm_phase1.sh
SCHEDULE_NAME=bulk-inference-phase1-schedule
SCHEDULE_START_AT='10 0 1,15 * *'
SCHEDULE_STOP_AT='0 21 1,15 * *'
