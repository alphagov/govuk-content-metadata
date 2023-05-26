## Google Workflow for post named-entity extraction processing (bulk inference)

**Important Note**: Originally, this workflow was set to automatically run as part of the NER bulk inference pipeline on the 1st and 15th of each month at 22:00. This scheduled execution has now been deactivated since the deployment of the NER new-content-only daily inference pipeline.

### Workflow specifics

A [Google Workflow](https://cloud.google.com/workflows/docs/overview) orchestrates the named entities post-extraction processing for the bulk inference pipeline.

The workflow consists of three steps and can be found in the [src/post_extraction_process/post-extraction-gc-workflow.yaml](src/post_extraction_process/post-extraction-gc-workflow.yaml) file.

The three steps are:

1. Create the `named_entities.named_entities_all` BigQuery table. This includes noise removal of raw entities and creation of a unique url for each tagged entity name.

2. Create the `named_entities.named_entities_counts` BigQuery table; aggregation and count of tagged entity per gov.uk page.

3. Transfer of the `named_entities_counts` BigQury table to a CSV.GZ file in Google storage.


### How to deploy the workflow

1. Ensure secret variables are loaded to your environment. From the root directory in this repository:
```shell
direnv allow
```

2. Change the value of any environment variables that need updating (e.g., START TIME) by modifying the file [src/post_extraction_process/vars_config.sh](/src/post_extraction_process/vars_config.sh).


3. Load the environment variables:
```shell
source src/post_extraction_process/vars_config.sh
```

4. Deploy the workflow to GCP by executing:

```sh
bash src/post_extraction_process/deploy_post_extraction_gc_workflow.sh
```

### Set up the Cloud Scheduler job that triggers your workflow

Originally, a Scheduler ran the post-extraction workflow upon the completion
of the NER bulk inference pipeline, at a specified time. This scheduled execution has now been deactivated.

To re-add a Scheduler, update the value of the `BULK_POSTPROC_START_TIME` environemnt variable in[src/post_extraction_process/vars_config.sh](/src/post_extraction_process/vars_config.sh), and execute the command:
```sh
bash src/post_extraction_process/schedule_post_extraction_gc_workflow.sh
```

### To excute the workflow on-demand

To execute the workflow outside of the schedule, from the terminal run:

```shell
gcloud workflows run ${BULK_POSTPROC_WORKFLOW_NAME} \
--call-log-level="log-all-calls"
```

or go to the [Workflows page in the Google Console](https://console.cloud.google.com/workflows), select the workflow and click on "Execute".
