#!/bin/bash

# usage="Script to extract entities from pages on GOV.UK and stream output upload to Google Storage."

# The following options are available:
#  -m    full path to NER model to use for inference.  (Required)
#  -p    one of 'title', 'description', 'text' (Required)
#  -b    batch size; number of texts to be batched processed by the Spacy pipeline (Optional)
#  -n    number of cores for the parallel processing of texts (Optional)

# Requirements:
# - Ensure you meet all the `README.md/Inference pipeline [cloud]` requirements.

# The script consists of 3 steps:
# - Create input content data tables in Google Big Query
# - Run NER (bulk) inferential pipeline
# - Stream uploading of outcome files with extracted entities to Google Storage
# - Transfer the extracted entities files into corresponding BigQuery tables


# Set default value for `date` to today in the format `DDMMYY`
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     TODAY=$(date '+%d%m%y');;
    Darwin*)    TODAY=$(date -v '+%d%m%y');;
    *)          TODAY="UNKNOWN:${unameOut}"
esac


while getopts ":m:b:n:" opt; do
    case $opt in
        m)
            echo "argument -m called with value $OPTARG" >&2
            NER_MODEL="${OPTARG}"
            ;;
        b)
            BATCH_SIZE="${OPTARG}"
            echo "argument -b called with value $OPTARG" >&2
            ;;
        n)
            N_PROC="${OPTARG}"
            echo "argument -n called with value $OPTARG" >&2
            ;;
        *)
            echo "invalid command: no parameter included with argument $OPTARG"
            ;;
  esac
done


echo "Creating input files in Google Big Query"
python -m src.create_input_files
echo "Input files created."

echo "Running NER bulk inferential pipeline and streaming upload to Google Storage"

echo "Starting NER bulk inferential pipeline for: 'title'"
python -m src.extract_entities_cloud -p "title" -m ${NER_MODEL} -d ${TODAY} -b ${BATCH_SIZE} -n ${N_PROC}
echo "Inference completed and data uploaded for: 'title'"

echo "Starting NER bulk inferential pipeline for: 'description'"
python -m src.extract_entities_cloud -p "description" -m ${NER_MODEL} -d ${TODAY} -b ${BATCH_SIZE} -n ${N_PROC}
echo "Inference completed and data uploaded for: 'description'"

echo "Starting NER bulk inferential pipeline for: 'text'"
python -m src.extract_entities_cloud -p "text" -m ${NER_MODEL} -d ${TODAY}
echo "Inference completed and data uploaded for: 'text'"


echo "Export entities to Big Query"
bq load --replace --source_format=NEWLINE_DELIMITED_JSON named_entities_raw.title gs://cpto-content-metadata/content_ner/entities_${TODAY}_title.jsonl entities_bq_schema
bq load --replace --source_format=NEWLINE_DELIMITED_JSON named_entities_raw.description gs://cpto-content-metadata/content_ner/entities_${TODAY}_description.jsonl entities_bq_schema
bq load --replace --source_format=NEWLINE_DELIMITED_JSON named_entities_raw.text gs://cpto-content-metadata/content_ner/entities_${TODAY}_text.jsonl entities_bq_schema
echo "Entities exported successfully to Big Query"
