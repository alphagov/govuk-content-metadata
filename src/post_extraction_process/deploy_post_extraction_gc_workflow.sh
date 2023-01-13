gcloud workflows deploy entities-post-processing-workflow \
    --source=post-extraction-gc-workflow.yaml \
    --location=europe-west2 \
    --service-account=cpto-content-metadata-sa@cpto-content-metadata.iam.gserviceaccount.com \
    --description="Post-extraction processing and aggregation of named -entities in Big Query and export of counts table to Google Storage"
