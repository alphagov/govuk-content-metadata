"""
Helper python script to create the Request JSON body needed by Vertex AI
BatchPredictions REST API.

Given a configuration YAML file,
returns the Request JSON body file that can be used by Vertex AI API to send batch
prediction requests.

The script takes the following positional arguments:

- config_filepath: filepath to the configuration YAML file (incl. extension)
- output_folder [optional, default = "json_files"]: filepath to folder where to save the JSON file


To run:

```shell
cd inference_pipeline_new_content
python utils/create_json_request_body.py \
  "utils/request_json_config.yml"
```

References
https://cloud.google.com/vertex-ai/docs/predictions/get-predictions#retrieve_batch_prediction_results
https://cloud.google.com/vertex-ai/docs/reference/rest/v1beta1/projects.locations.batchPredictionJobs#instanceconfig
https://cloud.google.com/vertex-ai/docs/reference/rest/v1beta1/projects.locations.models#Model.FIELDS.supported_input_storage_formats
https://cloud.google.com/vertex-ai/docs/reference/rest/v1beta1/projects.locations.batchPredictionJobs#instanceconfig
https://cloud.google.com/vertex-ai/docs/predictions/get-predictions#aiplatform_batch_predict_custom_trained-drest
https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/official/prediction/custom_batch_prediction_feature_filter.ipynb

Note from:
https://cloud.google.com/vertex-ai/docs/reference/rest/v1beta1/BigQueryDestination
When only the project is specified, the Dataset and Table is created. When the full table reference is specified,
the Dataset must exist and table must not exist.
"""

import json
import yaml
import typer
from pathlib import Path


def main(
    config_filepath: Path = typer.Argument(..., exists=True, dir_okay=False),
    output_filepath: Path = typer.Argument(
        "json_files/request_daily_ner.json", dir_okay=False
    ),
) -> None:
    """
    Given a a configuration YAML file,
    returns the Request JSON body file that can be used by Vertex AI API to send batch
    prediction requests for that part of page.

    Args:
      config_filepath: filepath to the configuration YAML file (incl. extension)
      output_folder: filepath to the output JSON file (default: 'json_files/request_daily_ner.json')

    Returns:
      None. Saved the output JSON to the specified output_filepath.
    """

    with open(config_filepath, "r") as file:
        config = yaml.safe_load(file)

    input = config["input"]

    json_string = {
        "displayName": f"{input['BATCH_JOB_NAME']}",
        "model": f"projects/{input['PROJECT_ID']}/locations/{input['REGION']}/models/{input['MODEL_ID']}",
        "inputConfig": {
            "instancesFormat": input["INPUT_FORMAT"],
            "bigquerySource": {"inputUri": input["INPUT_TABLE_URI"]},
        },
        "outputConfig": {
            "predictionsFormat": input["OUTPUT_FORMAT"],
            "bigqueryDestination": {"outputUri": input["OUTPUT_TABLE_URI"]},
        },
        "dedicatedResources": {
            "machineSpec": {
                "machineType": input["MACHINE_TYPE"],
            },
            "startingReplicaCount": input["MIN_NODES"],
            "maxReplicaCount": input["MAX_NODES"],
        },
        "manualBatchTuningParameters": {"batch_size": input["BATCH_SIZE"]},
        "instanceConfig": {
            "instanceType": "object",
            "includedFields": input["INCLUDED_FIELDS"],
        },
    }

    with open(f"{output_filepath}", "w") as outfile:
        json.dump(json_string, outfile)


if __name__ == "__main__":  # noqa: C901
    typer.run(main)
