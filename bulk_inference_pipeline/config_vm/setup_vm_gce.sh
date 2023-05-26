#! /bin/bash

# General info
# This script does:
# 1. Install NVIDIA CUDA driver and toolkit
# 2. Install Docker and NVIDIA container runtime
# 3. Authenticate Docker via the pre-installed gcloud cli and the attached service account

# 1. install NVIDIA CUDA driver and toolkit

# On your VM, download and install the CUDA toolkit.
# Here: GPU type = NVIDIA T4, OS = Linux Ubuntu 20.04
# from : https://developer.nvidia.com/cuda-downloads?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=20.04&target_type=deb_network
# https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html

# Install GCC
sudo apt update
sudo apt install -y build-essential

echo "Verify GPU is CUDA compatible"
lspci | grep -i nvidia
echo "Verify you have a supported version of Linux"
uname -m && cat /etc/*release
echo "Verify the system has gcc installed"
gcc --version
echo "Verify the System has the Correct Kernel Headers and Development Packages Installed"
uname -r
# The kernel headers and development packages for the currently running kernel can be installed with:
# sudo apt-get install linux-headers-$(uname -r)

echo "Remove Outdated Signing Key"
sudo apt-key del 7fa2af80

echo "Installation of Nvidia CUDA..."
# Most recent version
# wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb
# sudo dpkg -i cuda-keyring_1.0-1_all.deb
# sudo apt-get update
#sudo apt-get -y install cuda

echo "Installing CUDA version 11.7.0"
# from:  https://developer.nvidia.com/cuda-11-7-0-download-archive?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=20.04&target_type=deb_local
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/11.7.0/local_installers/cuda-repo-ubuntu2004-11-7-local_11.7.0-515.43.04-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu2004-11-7-local_11.7.0-515.43.04-1_amd64.deb
sudo cp /var/cuda-repo-ubuntu2004-11-7-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda

echo "Add CUDA to the PATH"
# from https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html#post-installation-actions
# Environment set-up
# if cuda 11.7
export PATH=/usr/local/cuda-11.7/bin${PATH:+:${PATH}}

echo "Checks that CUDA was installed successfully"
# Verify the installation
# https://cloud.google.com/compute/docs/gpus/install-drivers-gpu#verify-driver-install
nvcc --version
sudo nvidia-smi
# The NVIDIA Persistence Daemon should be automatically started for POWER9 installations. Check that it is running with the following command:
# systemctl status nvidia-persistenced
cat /proc/driver/nvidia/version


# 2. install Docker and NVIDIA container runtime

echo "Installing Docker and NVIDIA runtime..."
# https://docs.nvidia.com/ngc/ngc-vgpu-setup-guide/index.html

sudo apt-get install -y apt-transport-https\
 curl ca-certificates \
 software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository \
 "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

echo "Installing Docker Engine"
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "Verify that docker was installed successfully"
docker --version
docker compose version


# 3. Authenticate Docker

echo "Authenticate docker via the pre-installed gcloud cli and the attached service account..."
# OPTION: root user we could do it for the root user
# sudo su root -c 'gcloud auth configure-docker --quiet'
# gcloud auth configure-docker --quiet
# check added credentials
# sudo cat /root/.docker/config.json
# OPTION END

# OPTION: local user
# Add your user to the docker group:
echo $(whoami)
sudo usermod -a -G docker $USER
id
# IMPORTANT: You will need to reboot (ssh-out and then ssh-in again )

echo "Check your user is listed in the docker group"
grep docker /etc/group

echo "Authenticate docker via the pre-installed gcloud cli and the attached service account"
# ref: https://cloud.google.com/artifact-registry/docs/docker/pushing-and-pulling
gcloud auth configure-docker --quiet
# add permission for Artifect Registry
gcloud auth configure-docker europe-west2-docker.pkg.dev --quiet

echo "Verify permissions"
cat .docker/config.json

echo "Exposing GPU Drivers to Docker using the NVIDIA Toolkit..."
# The best approach is to use the NVIDIA Container Toolkit.
# The NVIDIA Container Toolkit is a docker image that provides support to automatically
# recognize GPU drivers on your base machine and pass those same drivers to your Docker container
# when it runs.

# If you are able to run nvidia-smi on your base machine,
# you will also be able to run it in your Docker container (and all of your programs will
# be able to reference the GPU).
# In order to use the NVIDIA Container Toolkit, you pull the NVIDIA Container Toolkit image
# at the top of your Dockerfile.

echo "Installing NVIDIA container runtime"
# https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
      && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
      && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2

# Restart Docker:
sudo systemctl restart docker

exit
