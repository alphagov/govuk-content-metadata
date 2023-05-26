## Create and set up the Virtual Machine (WM) on Google Compute Engine (GCE) - One off

Here we detail how to set up the Cloud Engine VM to execute the phase-1 and phase-2 NER bulk inference pipelines.

First of all, ensure the secret environment variables have been loaded. From this repository's root directory, run:

``shell
direnv allow
```

All the following commands are then run from the `bulk_inference_pipeline` subdirectory:

```shell
cd bulk_inference_pipeline
```

All the scripts are available in the [bulk_inference_pipeline/config_vm](/bulk_inference_pipeline/config_vm/) folder.


### 0. Set and upload the required environment variables

* Change the value of any environment variables that need updating (e.g., SCHEDULE_START_AT) by modifying the file [config_vm/env_vars_phase1.sh](/bulk_inference_pipeline/config_vm/env_vars_phase1.sh) if updating Phase-1 Entity inference pipeline or [config_vm/env_vars_phase2.sh](/bulk_inference_pipeline/config_vm/env_vars_phase2.sh) for Phase-2 Entity inference pipeline.

* Load the variables, substituting N = 1 for phase-1 entities and N = 2 for phase-2 entities:
```shell
source config_vm/env_vars_phase${N}.sh
```


### 1. Create the general Ubuntu VM on GCE

From the terminal:

```shell
bash config_vm/create_vm_gce.sh
```

Then wait 15 sec before executing the rest to ensure the VM is up and running before ssh-ing into it

### 2. Set up the VM

* Transfer the set-up file to the VM:

```shell
gcloud compute scp config_vm/setup_vm_gce.sh ${VM_NAME}:~ --zone=${ZONE}
```

* Connect to the VM and run the set-up script:

```shell
gcloud compute ssh ${VM_NAME} --zone=${ZONE} --command="bash setup_vm_gce.sh" -- -t
```

The set-up script will:
- install NVIDIA CUDA driver and toolkit
- install Docker and NVIDIA container runtime
- Authenticate Docker via the pre-installed gcloud cli and the attached service account.


### 3. Add the start-up script

The start-up script launches the specified docker image every time the VM is started.

* Create the bash start-up script for the intended phase entity by running in your terminal:

```shell
envsubst '$DOCKER_IMAGE_NAME'  <config_vm/template_startup_script_vm.txt > config_vm/startup_script_vm.sh
```

This will substitute the value of the bash environment variable $DOCKER_IMAGE_NAME into the script and
save it to a new (bash) file called `config_vm/startup_script_vm.sh`.

* Add the start-up script to the VM

```shell
bash config_vm/add_startup_script_to_vm.sh
```

**Note**: Every time you modify anything in the start-up script, you'll need to re-add it to the VM instance using step (3).


### 4. Add a scheduled execution to the VM instance

* If needed, modify the values of `SCHEDULE_START_AT` and `SCHEDULE_STOP_AT` in [config_vm/env_vars_phase1.sh](/bulk_inference_pipeline/config_vm/env_vars_phase1.sh) for updating Phase-1 Entity inference pipeline and [config_vm/env_vars_phase2.sh](/bulk_inference_pipeline/config_vm/env_vars_phase2.sh) for Phase-2 Entity inference pipeline.

* Attach the schedule to the VM:
```shell
bash config_vm/add_schedule_policy_to_vm.sh
```

The inference pipeline is now scheduled to run according to the schedule.

Reference: [compute/instances/schedule-instance-start-stop](https://cloud.google.com/compute/docs/instances/schedule-instance-start-stop).


### 5. (Optional) Monitor the start-up script and execution of the docker image

Wait ~15sec, then you can connect to the VM and monitor the execution of the start-up script
```shell
gcloud compute ssh --project=cpto-content-metadata --zone=${ZONE} ${VM_NAME}
sudo journalctl -u google-startup-scripts.service -n 200 -f
```

Reference: [startup-scripts/linux#viewing-output](https://cloud.google.com/compute/docs/instances/startup-scripts/linux#viewing-output).


### 6. Delete the VM after execution

Please delete the VM (and attched boot disk) after the execution is terminated, or remove the attached execution schedule.
