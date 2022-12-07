# Create and set up the Virtual Machine (WM) on Google Compute Engine (GCE) - One off

Here we detail how the VM was created and set. There is no need to repeat these steps as they are one off.

All the commans were run from the `bulk_inference_pipeline` subdirectory:

```shell
cd bulk_inference_pipeline
```

All the scripts are available in the `cpto-content-metadata` Google Storage bucket.
This only works if you have the permissions

```shell
gsutil -m cp -r gs://cpto-content-metadata/gce_vm_bulk_inference_phase1_configs/* config_vm
```

NOTE - Set variables:
VM_NAME=<name-of-virtual-machine>

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


3. Stop the instance, add the start-up script and a schedule to the VM instance.

The start-up script launches the docker image every time the VM is started.

```shell
bash config_vm/create_schedule_policy_vm.sh
```

The inference pipeline is now scheduled to run according to the schedule specified in config_vm/create_schedule_policy_vm.sh. No manual actions needed.


4. (Optional) Monitor the start-up script and execution of the docker image

Connect to the VM and monitor the start-up script
```shell
gcloud compute ssh --project=cpto-content-metadata --zone=europe-west2-a ${VM_NAME}
sudo journalctl -u google-startup-scripts.service -n 200 -f
```

Ref: https://cloud.google.com/compute/docs/instances/startup-scripts/linux#viewing-output
