# `fast_api_model_serving` folder overview

## Overview

This folder contains the required files to deploy a HTTPS server to serve predictions for the projects fine-tuned
models.

It contains components:
- `main.py`: The Fast API implementation for serving NER predictions from requests.
- `Dockerfile`: A docker file for building a Docker image to build everything needed to run the API, so it
  can be pushed to GCP.
- `cloudbuild.yaml`: GCP Cloud Build configuration file to automate steps to build and push the docker image to
  GCP. Crucially, this file also downloads the model from GCP into the image as it is being build. This is more
  efficient than downloading at runtime inside the `main.py` script.

## Prerequisites
- Access to the `cpto-content-metadata` project on GCP
- GCP authentication. Run

```bash 
gcloud auth login

## To run the Fast API locally
Before anything, you may want to run the Fast API locally, to test or during development.
To do so, make sure you have the model downloaded.
From the folder root, run:

```shell
gsutil cp -r gs://cpto-content-metadata/models/mdl_ner_trf_b1_b4/model-best .
```

Then run:

```shell
uvicorn --host 0.0.0.0 main:app --port 8080 --reload
```

A server should start at `http://0.0.0.0:8080`

From here you can interact with the API. Any changes to the code should be reflected in real time, useful for dev.

Delete the downloaded model before pushing to GCP!

## To push the model to a GCP image registry:

First make sure the only files in the folder are:
- cloudbuild.yaml
- main.py
- Dockerfile

To start the build and push process on GCP, run:
```shell
gcloud builds submit --config cloudbuild.yaml
```

When finished, you will be able to see the model container on the GCP container registry.

## Using the API for model inference in Vertex

Following the above steps, you will push your image into an image registry on GCP.
In vertex AI, navigate to the Model Registry sub-directory, and at the top click on the `Import` option.
Complete the configuration as required. This is comuplsory if you are using a custom model - something built using Fast API or similar - however, if you are using a Tensorflow or Sklearn model, you may not have to do this - see https://cloud.google.com/vertex-ai/docs/training/overview.

This registers the model on Vertex, which can then be used for Online (realtime) and Batch prediction jobs.
For this project, it will usually be the latter.
Follow the instructions for each on the console depending on your use case.

## IMPORTANT CONSIDERATIONS

GCP requires specific input payload structure for custom ML models.
The output of the Fast API prediction model should be a dictionary of key-value pairs.
This will be formated by GCP as below:
```
{"instance":
    [
        {"your_key1": "your_value1"},
        {"your_key2": "your_value2"},
        {"your_key3": "your_value3"},
        ...
    ]}
```
See https://cloud.google.com/vertex-ai/docs/predictions/get-predictions#formatting-instances-as-json for more datails.
