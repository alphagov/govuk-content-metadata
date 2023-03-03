# Google Workflow for post named-entity extraction processing

A [Google Workflow](https://cloud.google.com/workflows/docs/overview) orchestrates the named entities post-extraction processing.

The workflow consists of three steps and can be found in the [src/post_extraction_process/post-extraction-gc-workflow.yaml](src/post_extraction_process/post-extraction-gc-workflow.yaml) file.

The three steps are:

1. Create the `named_entities.named_entities_all` BigQuery table. This includes noise removal of raw entities and creation of a unique url for each tagged entity name.

2. Create the `named_entities.named_entities_counts` BigQuery table; aggregation and count of tagged entity per gov.uk page.

3. Transfer of the `named_entities_counts` BigQury table to a CSV.GZ file in Google storage.


## How we deployed the workflow

From the `src/post_extraction_process` sub-directory:
```sh
cd src/post_extraction_process
```

To gcloud CLI command to deploy the workflow to GCP is in `deploy_post_extraction_gc_workflow.sh`. To execute it:

```sh
bash deploy_post_extraction_gc_workflow.sh
```

## How we created a Cloud Scheduler job that triggers your workflow

We have created a Scheduler that runs the post-extraction workflow upon the completion
of the bulk inference pipeline, i.e. the 1st and 15th of each month at 22:00.

To add the Scheduler, we executed the command:
```sh
bash schedule_post_extraction_gc_workflow.sh
```

## To excute the workflow on-demand

To execute the workflow outside of the schedule, from the terminal run:

```shell
gcloud workflows run entities-post-processing-workflow \
--call-log-level="log-all-calls
```

or go to the [Workflows page in the `cpto-content-metadata` Google Console](https://console.cloud.google.com/workflows), select the workflow and click on "Execute".
