VM_NAME=bulk-inference-phase2-ubuntu-gpu
DOCKER_IMAGE_NAME=ner-bulk-inference-phase2
STARTUP_SCRIPT_PATH=config_vm/startup_script_vm_phase2.sh
SCHEDULE_NAME=bulk-inference-phase2-schedule
SCHEDULE_START_AT='30 22 1,15 * *'
SCHEDULE_STOP_AT='30 20 2,16 * *'
