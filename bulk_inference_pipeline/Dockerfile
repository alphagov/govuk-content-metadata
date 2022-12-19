FROM nvidia/cuda:11.2.1-runtime-ubuntu20.04

WORKDIR /infer
ENV PYTHONUNBUFFERED=1

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/London
RUN apt update && apt-get install -y apt-transport-https && \
    apt install --no-install-recommends -y build-essential software-properties-common && \
    add-apt-repository -y universe && \
    apt install --no-install-recommends -y python3.9 python3-pip python3-setuptools python3-distutils && \
    apt-get install -y curl && curl -sSL https://sdk.cloud.google.com | bash && \
    apt clean && rm -rf /var/lib/apt/lists/*
# Adding the package path to local
ENV PATH=$PATH:/root/google-cloud-sdk/bin

COPY requirements-inference-bulk.txt .

RUN python3.9 -m pip install --upgrade pip && \
    python3.9 -m pip install --no-cache-dir -r requirements-inference-bulk.txt

COPY . .

RUN ls --recursive .

# Note, the value is set at build-time in cloudbuild.yaml file
ARG phaseN
ENV envPhaseN=$phaseN

ENTRYPOINT []
RUN chmod +x extract_entities_cloud.sh
CMD bash ./extract_entities_cloud.sh -m "models/model-best" -h ${envPhaseN}
