# `ner_streamlit_app` folder overview

This folder is used to create a streamlit web app to visualise NER outputs.

Prerequisites:
- Authenticate yourself in google using the CLI
- Have access to the GCP project `cpto-content-metadata`
```
gcloud auth login
```

To test locally, build the docker image using

```
docker build -t streamlit-app .
```

then run the image with

```
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
