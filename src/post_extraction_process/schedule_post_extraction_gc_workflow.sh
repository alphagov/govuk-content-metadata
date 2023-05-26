gcloud scheduler jobs create http $BULK_POSTPROC_WORKFLOW_NAME \
--schedule="${BULK_POSTPROC_START_TIME}" \
--uri="https://workflowexecutions.googleapis.com/v1/projects/cpto-content-metadata/locations/${REGION}/workflows/${BULK_POSTPROC_WORKFLOW_NAME}/executions" \
--time-zone="Europe/London" \
--location=${REGION} \
--oauth-service-account-email=${NER_BULK_INFERENCE_SA}
