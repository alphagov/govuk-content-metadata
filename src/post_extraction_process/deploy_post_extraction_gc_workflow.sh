gcloud workflows deploy ${BULK_POSTPROC_WORKFLOW_NAME} \
    --source=${BULK_POSTPROC_WORKFLOW_YAML_PATH} \
    --location=${REGION} \
    --service-account=${NER_BULK_INFERENCE_SA} \
    --description="Bulk post-extraction processing and aggregation of named-entities in Big Query and export of counts table to Google Storage"
