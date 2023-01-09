# Create and set up the Virtual Machine (WM) on Google Compute Engine (GCE) - One off

Here we detail how the VM was created and set. There is no need to repeat these steps as they are one off: PLEASE DO NOR RUN THEM AGAIN if the VM has already been set up correctly.

All the commands were run from the `bulk_inference_pipeline` subdirectory:

```shell
cd bulk_inference_pipeline
```

All the scripts are available in the [bulk_inference_pipeline/config_vm](bulk_inference_pipeline/config_vm) folder.


# 0. Set and upload the required environment variables

Open the `config_vm/env_vars.sh` file and update the value of the environment variables as necessary.

Then load the variables by running:
```shell
source config_vm/env_vars.sh
```

Open the `config_vm/startup_script_vm_gce.sh` file and set or update the value of the `DOCKER_IMAGE_NAME` variable (if needed).


# 1. Create the general Ubuntu VM on GCE

```shell
bash config_vm/create_vm_gce.sh
```

# 2. Set up the VM

Transfer the set-up file to the VM:

```shell
gcloud compute scp config_vm/setup_vm_gce.sh ${VM_NAME}:~ --zone=europe-west2-a
```

Connect to the VM and run the set-up script:

```shell
gcloud compute ssh ${VM_NAME} --zone=europe-west2-a --command="bash setup_vm_gce.sh" -- -t
```

The set-up script will:
- install NVIDIA CUDA driver and toolkit
- install Docker and NVIDIA container runtime
- Authenticate Docker via the pre-installed gcloud cli and the attached service account.


# 3. Stop the instance, add the start-up script and a schedule to the VM instance.

The start-up script launches the specified docker image every time the VM is started.

```shell
bash config_vm/create_schedule_policy_vm.sh
```

The start-up script defines which docker image to be launched every time the VM is started.
Please modify the script (`config_vm/startup_script_vm_gce.sh`) if you need a different docker image to be launched.

The inference pipeline is now scheduled to run according to the schedule specified in `config_vm/create_schedule_policy_vm.sh`; modify the schedule if needed. No manual actions needed.

Every time you modify anything in the start-up script, you'll need to re-add it to the VM instance using step (3).


# 4. (Optional) Monitor the start-up script and execution of the docker image

Wait ~15sec, then you can connect to the VM and monitor the execution of the start-up script
```shell
gcloud compute ssh --project=cpto-content-metadata --zone=europe-west2-a ${VM_NAME}
sudo journalctl -u google-startup-scripts.service -n 200 -f
```

Ref: https://cloud.google.com/compute/docs/instances/startup-scripts/linux#viewing-output
