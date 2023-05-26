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


# Bulk Inference pipeline [run on a VM with GPU on Google Compute Engine]

Inference pipeline to extract named entities from the whole GOV.UK content estate (in "bulk").
The pipeline is deployed in two Docker containers onto two Virtual Machine (VM) instances (one per phase-1 and one per phase-2 entities) on Google Compute Engine (GCE).

The bulk inference pipeline is now intended to be executed as a one-off, if either of the phase-1 entity or phase-2 entity models is retrained and re-deployed.

Please refer to the [bulk_inference_pipeline/README.md](/bulk_inference_pipeline/README.md) for complete documentations.
