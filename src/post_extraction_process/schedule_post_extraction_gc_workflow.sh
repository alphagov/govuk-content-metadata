gcloud scheduler jobs create http post-extraction-process-2-and-16-of-month-at-21-30 \
--schedule="30 21 2,16 * *" \
--uri="https://workflowexecutions.googleapis.com/v1/projects/cpto-content-metadata/locations/europe-west2/workflows/entities-post-processing-workflow/executions" \
--time-zone="Europe/London" \
--location=europe-west2 \
--oauth-service-account-email="cpto-content-metadata-sa@cpto-content-metadata.iam.gserviceaccount.com"
