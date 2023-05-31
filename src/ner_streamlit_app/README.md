# `ner_streamlit_app` folder overview

This sub-directory contains the code and requirements we developed to create a [Streamlit](https://streamlit.io/) app to visualise NER outputs. This is an interactive web application built with the aim to help prospective users understand how NER works via visualisation and user interaction.


## Software / tools

- Docker
- Python 3.9

Python package dependencies are defined in [requirements.txt](/src/ner_streamlit_app/requirements.txt).


## Building and testing the app locally

Prerequisites:
- Authenticate yourself in google using the CLI
- Have access to the GCP project `cpto-content-metadata`

```shell
gcloud auth login
```

To test locally, build the docker image using

```shell
docker build -t streamlit-app .
```

then run the image with

```shell
docker run -v "$HOME/.config/gcloud:/gcp/config:ro" \
-v /gcp/config/logs \
--env GCLOUD_PROJECT=cpto-content-metadata \
--env CLOUDSDK_CONFIG=/gcp/config \
--env GOOGLE_APPLICATION_CREDENTIALS=/gcp/config/application_default_credentials.json \
-d -p 8501:8501 \
streamlit-app
```

The local volume mounts such as `"$HOME/.config/gcloud` are generated when you authenticate with gcloud in step 1 above.
This is also the case for the environment variables below. These are all generated in the users home directory, provided they
have authenticated to gcloud.


## Deployment via Google Cloud Platform

### Techstack and GCP roles

The app deployment requires access to/ use of the following tools:

- Artefact Registry, repository `europe-west2-docker.pkg.dev/cpto-content-metadata/cpto-content-metadata-docker-repo/ner-streamlit-app`
- Google Storage bucket `gs://cpto-content-metadata` and objects `gs://cpto-content-metadata/content_ner/phase2_ner_trf_model` and ``gs://cpto-content-metadata/content_ner/phase2_ner_trf_model`
- [Cloud Run](https://cloud.google.com/run)
- GitHub Actions for continous deployment.

The app deployment is managed through a user-created GCP service account with the following roles/permissions:

- roles/storage.buckets.get (for the `gs://cpto-content-metadata/models/` bucket)
- roles/artifactregistry.reader (for the `europe-west2-docker.pkg.dev/cpto-content-metadata/cpto-content-metadata-docker-repo` Artefact Registry repository)

The custom service account has been further set up as "iam.workloadIdentityUser" via Workload Identity Federation to authenticate and authorise GitHub Actions Workflows to Google Cloud. This was set up by following the official documentations [github/setting-up-workload-identity-federation](https://github.com/google-github-actions/auth#setting-up-workload-identity-federation) and [gcp/workload-identity-federation-with-deployment-pipelines](https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines).


### GitHub Secrets

The application depends on two secret values having been set as environment variables.

<details>
 <summary>Secrets</summary>

 - `GCP_NER_APP_SA`: GCP custom service account for the streamlit app (full email address);

 - `GCP_GITHUB_WORKLOAD_IDENTITY_PROVIDER`: (Github) Workload Identity Provider source ID, in the format `projects/${GCP-PROJECT-NUMBER}/locations/global/workloadIdentityPools/${GCP-PROJECT-NAME}/providers/${WIP-PROVIDER-NAME}`.

 </details>


### Continuous Deployment

The following Github Action workflows are in use by the pipeline:

- [GCP-Deploy.yml](../.github/workflows/.github/workflows/GCP-Deploy.yml):
    rebuilds the Docker image, push it to Artefact Registry and deploys the app via Cloud Run.
