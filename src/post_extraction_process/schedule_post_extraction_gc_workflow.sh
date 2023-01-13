gcloud scheduler jobs create http post-extraction-process-1-and-15-of-month-at-22 \
--schedule="00 22 1,15 * *" \
--uri="https://workflowexecutions.googleapis.com/v1/projects/cpto-content-metadata/locations/europe-west2/workflows/entities-post-processing-workflow/executions" \
--time-zone="Europe/London" \
--location=europe-west2 \
--oauth-service-account-email="cpto-content-metadata-sa@cpto-content-metadata.iam.gserviceaccount.com"
