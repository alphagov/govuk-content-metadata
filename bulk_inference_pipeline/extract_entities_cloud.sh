#!/bin/bash

# usage="Script to extract entities from pages on GOV.UK and load output upload to Google Storage."

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
# - Upload outcome files with extracted entities to Google Storage
# - Transfer the extracted entities files into corresponding BigQuery tables


# Set default value for `date` to today in the format `DDMMYY`
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     TODAY=$(date '+%d%m%y');;
    Darwin*)    TODAY=$(date -v '+%d%m%y');;
    *)          TODAY="UNKNOWN:${unameOut}"
esac


while getopts ":m:h:" opt; do
    case $opt in
        m)
            echo "argument -m called with value $OPTARG" >&2
            NER_MODEL="${OPTARG}"
            ;;
        h)
            echo "argument -h called with value $OPTARG" >&2
            PHASE_N="${OPTARG}"
            ;;
        *)
            echo "invalid command: no parameter included with argument $OPTARG"
            ;;
  esac
done


echo "Creating input files in Google Big Query"
python3.9 -m src.create_input_files
echo "Input files created."

echo "Starting NER bulk inferential pipeline and upload to Google Storage"

echo "Extracting entities from: TITLE"
python3.9 -m src.extract_entities_cloud -p "title" --phase ${PHASE_N} -m ${NER_MODEL} -d ${TODAY} -b 2000 -n 1
echo "Extraction completed."
echo "Uploading file to Google Storage"
gcloud storage cp entities_phase${PHASE_N}_${TODAY}_title.jsonl gs://cpto-content-metadata/content_ner
echo "Upload completed."
echo "Exporting entities to Big Query"
bq load --replace --project_id=cpto-content-metadata --source_format=NEWLINE_DELIMITED_JSON named_entities_raw.title_${PHASE_N} gs://cpto-content-metadata/content_ner/entities_phase${PHASE_N}_${TODAY}_title.jsonl entities_bq_schema
echo "Entities exported."
echo "Inference completed for: TITLE"
rm -f entities_phase${PHASE_N}_${TODAY}_title.jsonl

echo "Extracting entities from: DESCRIPTION"
python3.9 -m src.extract_entities_cloud -p "description" --phase ${PHASE_N} -m ${NER_MODEL} -d ${TODAY} -b 2000 -n 1
echo "Extraction completed."
echo "Uploading file to Google Storage"
gcloud storage cp entities_phase${PHASE_N}_${TODAY}_description.jsonl gs://cpto-content-metadata/content_ner
echo "Upload completed."
echo "Exporting entities to Big Query"
bq load --replace --project_id=cpto-content-metadata --source_format=NEWLINE_DELIMITED_JSON named_entities_raw.description_${PHASE_N} gs://cpto-content-metadata/content_ner/entities_phase${PHASE_N}_${TODAY}_description.jsonl entities_bq_schema
echo "Entities exported."
echo "Inference completed for: DESCRIPTION"
rm -f entities_phase${PHASE_N}_${TODAY}_description.jsonl

echo "Extracting entities from: TEXT"
python3.9 -m src.extract_entities_cloud -p "text" --phase ${PHASE_N} -m ${NER_MODEL} -d ${TODAY} -b 64 -n 1
echo "Extraction and upload to Google Storage completed."
echo "Exporting entities to Big Query"
bq load --replace --project_id=cpto-content-metadata --source_format=NEWLINE_DELIMITED_JSON named_entities_raw.text_${PHASE_N} gs://cpto-content-metadata/content_ner/entities_phase${PHASE_N}_${TODAY}_text_*.jsonl entities_bq_schema
echo "Entities exported."
echo "Inference completed for: TEXT"
