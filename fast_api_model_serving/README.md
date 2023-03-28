# `fast_api_model_serving` folder overview

## Overview

This folder contains the required files to build a Docker container image that deploys and runs an HTTP server to serve predictions for our custom-trained fine-tuned NER models.

It contains components:
- `main.py`: The Fast API implementation for serving NER predictions from requests.
- `Dockerfile`: A docker file for building a Docker image to build everything needed to run the API, so it can be deployed on GCP.
- `cloudbuild.yaml`: GCP Cloud Build configuration file to automate steps to build and push the docker image to GCP Artifact Registry. Crucially, this file also downloads the models from GCP Google Storage, where they are saved, into the image as it is being build. This is more efficient than downloading at runtime inside the `main.py` script.

## Prerequisites
- Access to the `cpto-content-metadata` project on GCP
- GCP authentication. Run

```bash
gcloud auth login
```

### Vertex AI - Custom container requirements for prediction

Our custom container was built following [GCP guidelines on how to use a custom container to serve predictions from a custom-trained model](https://cloud.google.com/vertex-ai/docs/predictions/custom-container-requirements). See also the [use-custom-container](https://cloud.google.com/vertex-ai/docs/predictions/use-custom-container) docs.


## To run the Fast API locally

Before anything, you may want to run the Fast API locally, to iterate development more quickly and test your model without incurring prediction costs.

To deploy your model to a local endpoint instead of an online endpoint:

- make sure you have the models downloaded:

```shell
gsutil cp -m -r gs://cpto-content-metadata/models/phase2_ner_trf_model ./models
gsutil cp -m -r gs://cpto-content-metadata/models/phase2_ner_trf_model ./models
```

- then from this sub-directory root, run:

```shell
uvicorn --host 0.0.0.0 main:app --port 8080 --reload
```

A server should start at `http://0.0.0.0:8080`.

The API documentation will be automatically created at `http://localhost:8080/docs`.

From here you can interact with the API. Any changes to the code should be reflected in real time, useful for dev.

Note: Delete the downloaded models before building and pushing the docker image to GCP!


## Push the model to GCP Artifact Registry:

First of all, ensure you are in the sub-directory root:

```shell
cd fast_api_model_serving
```

To build and push the docker image to GCP, run:

```shell
gcloud builds submit --config cloudbuild.yaml .
```

When finished, you will be able to see the model container on the project's GCP artifact registry.


## Using the API for model inference in GCP Vertex AI

Follow these steps after you have pushed the docker image to an image registry on GCP, as detailed in the previous section.


### Register your custom model

In vertex AI, navigate to the Model Registry sub-directory, and at the top click on the `Import` option.
Complete the configuration as required. This is compulsory if you are using a custom model - something built using Fast API or similar - however, if you are using a Tensorflow or Sklearn model, you may not have to do this - see https://cloud.google.com/vertex-ai/docs/training/overview.

This registers the model on Vertex, which can then be used for Online (realtime) and Batch prediction jobs.

### Realtime vs. Batch predictions

For the content metadata project, it will usually be Batch predictions.

To learn more, please see the following GCP's guidelines:
- [get-predictions](https://cloud.google.com/vertex-ai/docs/predictions/get-predictions)
- [get_batch_predictions](https://cloud.google.com/vertex-ai/docs/predictions/get-predictions#get_batch_predictions)
- [get_online_predictions](https://cloud.google.com/vertex-ai/docs/predictions/get-predictions#get_online_predictions)

Then follow the instructions for each on the console depending on your use case.

### How to make sure everything works as expected?

Even if your aim is to do Batch predictions, [it is recommend](https://medium.com/google-cloud/google-vertex-ai-batch-predictions-ad7057d18d1f) testing your model at least once in an online approach (deployed to Vertex AI Endpoint). This way, you can ensure the model runs successfully. Debugging is a lot easier as well.


### IMPORTANT CONSIDERATIONS: request and response body model for Vertex AI

GCP Vertex AI requires specific prediction request (input) and response (output) JSON format structure for custom ML models.

Please see [https://cloud.google.com/vertex-ai/docs/predictions/get-predictions#formatting-instances-as-json](https://cloud.google.com/vertex-ai/docs/predictions/get-predictions#formatting-instances-as-json) for more datails.
