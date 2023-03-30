# `fast_api_model_serving` folder overview

## Overview

This sub-directory contains the required files to build a Docker container image that deploys and runs an HTTP server to serve predictions for our custom-trained fine-tuned NER models.

The service is built on Fast API and uvicorn (see [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)).

The sub-directory contains the main components:
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

In particular, GCP Vertex AI requires specific prediction request (input) and response (output) JSON format structures for custom ML models.

Please see [https://cloud.google.com/vertex-ai/docs/predictions/get-predictions#formatting-instances-as-json](https://cloud.google.com/vertex-ai/docs/predictions/get-predictions#formatting-instances-as-json) for more datails.



## Development and testing phase

### Test the model API locally

During the development and testing phase, we can deploy our model to a local API endpoint. This allows to iterate development more quickly and test our model and API without incurring prediction costs.

To deploy your model to a local endpoint instead of an online endpoint:

- make sure you have the models downloaded:

```shell
cd fast_api_model_serving
gsutil -m cp -r gs://cpto-content-metadata/models/phase1_ner_trf_model ./models
gsutil -m cp -r gs://cpto-content-metadata/models/phase2_ner_trf_model ./models
```

- then from this sub-directory root, run:

```shell
uvicorn --host 0.0.0.0 main:app --port 8080 --reload
```

A server should start at `http://0.0.0.0:8080`.

The API documentation will be automatically created at `http://localhost:8080/docs`.

From here you can interact with the API. Any changes to the code should be reflected in real time, useful for dev.

Note: Delete the downloaded models before building and pushing the docker image to GCP!


## Deployment

### Push the model to GCP Artifact Registry:

This step is automated by [a GitHub Action workflow](../.github/workflows/build-upload-model-api-gcp.yaml); the docker image is built and pushed to GCP Artifact Registry
when a change is pushed to any file in this `fast_api_model_serving` sub-directory.

When finished, you will be able to see the model container on the project's GCP artifact registry.


### Register your custom model on Vertex

This registers the model on Vertex, which can then be used for Online (realtime) and Batch prediction jobs.

The step is automated by the [GitHub Action workflow](../.github/workflows/build-upload-model-api-gcp.yaml), which runs the bash script [deploy_to_vertexai.sh](deploy_to_vertexai.sh_) where the gcloud commands to upload the model are implemented.
Adapt the bash script if changes are needed.

Note that this is a compulsory step in that we are using a custom model and a custom container. However, if you are using a Tensorflow or Sklearn model, you may not have to do this - see https://cloud.google.com/vertex-ai/docs/training/overview.



### Using the API for model inference in GCP Vertex AI

#### Batch predictions

For the content metadata project, it will usually be Batch predictions.

For batch predictions, no extra set up is needed.

To learn more, please see the following GCP's guidelines:
- [get-predictions](https://cloud.google.com/vertex-ai/docs/predictions/get-predictions)
- [get_batch_predictions](https://cloud.google.com/vertex-ai/docs/predictions/get-predictions#get_batch_predictions)


#### Online (real-time) predictions

For online predictions, two extra steps must be take:
- Create a Vertex AI endpoint
- Deploy the model to the endpoint

These two steps have been implemented as optional options in the bash script [fast_api_model_serving/deploy_to_vertexai.sh](fast_api_model_serving/deploy_to_vertexai.sh).

To execute them, from the terminal in this subdirectiry run:
```shell
bash deploy_to_vertexai.sh --deploy
```

You can check progress by visiting https://console.cloud.google.com/vertex-ai/endpoints and https://console.cloud.google.com/vertex-ai/models.

To know more:
- [get_online_predictions](https://cloud.google.com/vertex-ai/docs/predictions/get-predictions#get_online_predictions)

As said, these steps are only needed for online (real-time) predictions
but they are good for testing and development so they are included in the bash script but as optional steps, and they are not run as part of our continous deployment workflow.


### How to make sure everything works as expected?

Even if our aim is to do Batch predictions, [it is recommend](https://medium.com/google-cloud/google-vertex-ai-batch-predictions-ad7057d18d1f) testing the model at least once in an online approach (deployed to Vertex AI Endpoint). This way, we can ensure the model runs successfully. Debugging is a lot easier as well.

IMPORTANT: Vertex AI endpoint is not a serverless service (so you always encounter some cost), thus, please remember to undeploy the model from the endpoint after done with your testing.
