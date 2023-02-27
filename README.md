# `govuk-content-metadata`

Project work related to extracting metdadata from gov.uk content.

```{warning}
Where this documentation refers to the root folder we mean where this README.md is
located.
```

## Getting started

To start using this project, [first make sure your system meets its
requirements](#requirements).

To be added.

### Requirements

```{note} Requirements for contributors
[Contributors have some additional requirements][contributing]!
```

- Python 3.9+ installed
- a `.secrets` file with the [required secrets and
  credentials](#required-secrets-and-credentials)
- [load environment variables][docs-loading-environment-variables] from `.envrc`

To install the Python requirements and pre-commit hooks, open your terminal and enter:

```shell
make requirements
```

or, alternatively, to only install the necessary Python packages using pip:

```shell
pip install -r requirements.txt
```

## Required secrets and credentials

To run this project, [you need a `.secrets` file with secrets/credentials as
environmental variables][docs-loading-environment-variables-secrets]. The
secrets/credentials should have the following environment variable name(s):

| Secret/credential | Environment variable name | Description                                |
|-------------------|---------------------------|--------------------------------------------|
| Prodigy License   | `PRODIGY_LICENSE`         | Digit code                                 |

Once you've added, [load these environment variables using
`.envrc`][docs-loading-environment-variables].

## Licence

Unless stated otherwise, the codebase is released under the MIT License. This covers
both the codebase and any sample code in the documentation. The documentation is ©
Crown copyright and available under the terms of the Open Government 3.0 licence.

# Data Version Control (DVC)

[DVC](dvc.org) is used in this project for version control of data and models.

Requirements:
- You must have read and write access to the [project GCP repository](gs://cpto-content-metadata)
- DVC installed with `pip install 'dvc[gs]'`
- Authenticated to used GCloud `gcloud auth application-default login`

The project uses two DVC remotes; for data and models, respectively.

To run:

1. Pull the latest models DVC
  ```shell
  dvc pull -r cpto-ner-dvc-models
  ```
2. Pull the latest training data DVC
  ```shell
  dvc pull -r cpto-ner-dvc-data
  ```

This should populate your local model and data folders from remote storage on GCP.

To commit/push the most recent data and models following updates. Use
```bash
dvc push
```
and
```bash
dvc pull
```
in place above.

For more information, visit [Syncing Data to GCP Storage Buckets](https://iterative.ai/blog/using-gcp-remotes-in-dvc)


# Inference pipeline [run on a VM with GPU on Google Compute Engine]

The pipeline is currently deployed in a Docker container onto a Virtual Machine (VM) instance on Google Compute Engine (GCE) within the `cpto-content-metadata` Google Project.

A schedule is associated to the VM which runs the pipeline twice a month, on the 1st and 15th of each month. To run the pipeline on an ad-hoc basis outside of this schedule, simply start the VM instance (please remember to turn it off!).

The GCE VM instance for the Phase-1 entities is called `bulk-inference-phase1-ubuntu-gpu`.

To know more about how to the VM was set up, please see [bulk_inference_pipeline/README.md](bulk_inference_pipeline/README.md).

## Pipeline Flow and Components

![BulkPipelineGCE](images/bulk_inference_pipeline_on_GCE_VM.png)

## Code and configuration files

All the code and configuration files are in the [bulk_inference_pipeline](bulk_inference_pipeline) subdirectory in this repository.

In particular:
- [bulk_inference_config.yml](bulk_inference_pipeline/bulk_inference_config.yml) contains the specification of the Google Cloud Projects and BigQuery datasets used by the pipeline;
- [entities_bq_schema](bulk_inference_pipeline/entities_bq_schema) contains the BigQuery table schema that is used to export the extracted entities (and their metadata) from the JSONL files in Google Storage to Big Query tables;
- [bulk_inference_pipeline/cloudbuild_phase*.yaml](bulk_inference_pipeline/cloudbuild_phase1.yaml) contains the steps to build and submit the Docker image for the bulk inference pipeline to Artifect registry. There is one such file for each entity phase.

## GCE VM specs

Full info can be found in the [bulk_inference_pipeline/README.md](bulk_inference_pipeline/README.md) file, and associated bash scripts in [bulk_inference_pipeline/config_vm](bulk_inference_pipeline/config_vm).

- machine-type: n1-standard-16
- image-family: ubuntu-2004-lts
- GPU: nvidia-tesla-t4
- boot-disk-size: 100GB

## Other System Requirements

- Google Project `cpto-content-metadata`
- Artefact Registry repository `europe-west2-docker.pkg.dev/cpto-content-metadata/cpto-content-metadata-docker-repo`
- Google Storage bucket `gs://cpto-content-metadata` and folder `gs://cpto-content-metadata/content_ner`
- Google BigQuery datasets `cpto-content-metadata.content_ner` and `cpto-content-metadata.named_entities_raw`

If you are contributing to / editing the pipeline:
- Docker

## Editing an existing pipeline

The pipeline relies on the availability of a spacy NER model which is downloaded when the pipeline's Docker image is built.
For each Entity Phase {N}, the model is defined in the `bulk_inference_pipeline/cloudbuild_phase{N}.yaml` file. For instance, for Phase-1 entities, this is the [bulk_inference_pipeline/cloudbuild_phase1.yaml](bulk_inference_pipeline/cloudbuild_phase1.yaml) file.

Please update the relevant `cloudbuild_phase{N}.yaml` and rebuild the image if the model (or anything in the pipeline code) changes.

## Required Permissions

To run the pipeline on GCP, the inference uses the `cpto-content-metadata-sa` service account associated to the `cpto-content-metadata` Google Project. The following permissions must be enabled:

- Storage Object Creator (roles/storage.objects.create) - required to enable writing of pipeline outputs to Google Storage
- BigQuery Data Editor (roles/bigquery.tables.create) - required to read / create / write to output tables
- Compute Admin (roles/compute.admin) - required to create / edit / delete Compute Engine VMs and Compute Disks

And, in addition:

- Artifact Registry Reader (roles/artifactregistry.reader) for the `europe-west2-docker.pkg.dev/cpto-content-metadata/cpto-content-metadata-docker-repo` Artefact Registry repository.
- BigQuery Data Reader (roles/bigquery.dataViewer) for the `govuk-knolwedge-graph.content dataset` dataset in BigQuery

## Editing and re-deplying the pipeline to GCE

After you have done with your editing to the pipeline, you need to re-build the container image and publish it to Artifact Registry so that this will be pulled from the repository and launched when the VM is started.

Ensure you are in the sub-directory that contains the `Dockerfile`:
```shell
cd bulk_inference_pipeline
```

Re-build and re-publish the container image:
```shell
gcloud builds submit --config cloudbuild_phase{N}.yaml .
```
where `{N}` is the Entity Phase number, e.g. 1.


## Creating the pipeline for a new Entity phase

If you need to build the pipeline for a new Entity Phase:

- simply create a new `bulk_inference_pipeline/cloudbuild_phase{N}.yaml`, seeting `{N}` appropriately, and update the relevant values with that phase's information (i.e., model filepath, Docker image name, phase number);

- then set up a new VM in GCE and attached schedule, following the instructions in [bulk_inference_pipeline/README.md](bulk_inference_pipeline/README.md).


# Inference pipeline [run on a local machine]

We do not recommend to run the pipeline locally, unless you have a GPU available.

## Required Permissions

In order to run the pipeline's computations on a local machine (rather than a GCE VM), it is necessary to have a Google account with the following permissions enabled:

- Storage Object Creator (roles/storage.objects.create) - required to enable writing of pipeline outputs to Google Storage for the `cpto-content-metadata` project;
- BigQuery Data Editor (roles/bigquery.tables.create) - required to read / create / write to output tables for the `cpto-content-metadata` project;
- BigQuery Data Reader (roles/bigquery.dataViewer) for the `govuk-knolwedge-graph.content dataset` dataset in BigQuery.
- Artifact Registry Reader (roles/artifactregistry.reader) for the `europe-west2-docker.pkg.dev/cpto-content-metadata/cpto-content-metadata-docker-repo` Artefact Registry repository.

## Google Cloud authentication

The Google Cloud SDK is required to enable authentication with GCP on a local machine. Installation instructions for Mac (Brew) can be found [here](https://formulae.brew.sh/cask/google-cloud-sdk).

The following command can be used to authenticate with GCP:

```shell
gcloud auth login
```
then ensure your Project is set to `cpto-content-metedata`.

## Run the pipeline

```shell
docker run -v "$HOME/.config/gcloud:/gcp/config:ro" \
    -v /gcp/config/logs \
    --env GCLOUD_PROJECT=cpto-content-metadata \
    --env CLOUDSDK_CONFIG=/gcp/config \
    --env GOOGLE_APPLICATION_CREDENTIALS=/gcp/config/application_default_credentials.json \
    europe-west2-docker.pkg.dev/cpto-content-metadata/cpto-content-metadata-docker-repo/<DOCKER_IMAGE_NAME>
```

where <DOCKER_IMAGE_NAME> is the name of the pipeline's docker image.


# Named entities: Post-extraction processing and aggregation

After the named entities are extracted by the model and uploaded to tables in the BigQuery `cpto-content-metadata.named_entities.named_entities_raw` dataset, the outputs undergoes further processing and aggregation.

This post-extraction processing are executed by a google Workflow which is scheduled to run twice a month 1h after the bulk inference pipeline is expected to be finished.

All information about the post-extraction Workflow can be found in the [src/post_extraction_process](src/post_extraction_process) sub-directory.

The Workflow produces two BigQuey tables:

1. `cpto-content-metadata.named_entities.named_entities_all`:  one line per individual entity instance with as much noise as possible removed;

2. `cpto-content-metadata.named_entities.named_entities_counts`: aggregated table of counts of entity-type per url;

Table (2.) is then exported to a CSV.GZ file to a Google Storage bucket [gs://cpto-content-metadata/named_entities_counts/named_entities_counts.csv.gz](gs://cpto-content-metadata/named_entities_counts/named_entities_counts.csv.gz) that it is ready for govGraph ingestion.
