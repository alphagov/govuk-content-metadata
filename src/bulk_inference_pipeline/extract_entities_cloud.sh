#!/bin/bash

usage="Script to extract entities from pages on GOV.UK and stream output upload to Google Storage."

# The following options are available:
#  -m    full path to NER model to use for inference.  (Required)
#  -p    one of 'title', 'description', 'text' (Required)

# Requirements:
# - Ensure you meet all the `README.md/Inference pipeline [local machine]/Requirements`.

# The script consists of 3 steps:
# - Create input content data tables in Google Big Query
# - Run NER (bulk) inferential pipeline
# - Stream uploading of outcome files with extracted entities to Google Storage


# Set default value for `date` to yesterday in the format `DDMMYY`
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     YESTERDAY=$(date -d '-1 day' '+%d%m%y');;
    Darwin*)    YESTERDAY=$(date -v '-1d' '+%d%m%y');;
    *)          YESTERDAY="UNKNOWN:${unameOut}"
esac


while getopts ":m:p:" opt; do
    case $opt in
        m)
            echo "argument -m called with value $OPTARG" >&2
            NER_MODEL="${OPTARG}"
            ;;
        p)
            echo "argument -p called with value $OPTARG" >&2
            PART_OF_PAGE="${OPTARG}"
            ;;
        *)
            echo "invalid command: no parameter included with argument $OPTARG"
            ;;
  esac
done


echo "Creating input files in Google Big Query"
python create_input_files.py

echo "Running NER bulk inferential pipeline and streaming upload to Google Storage"
python extract_entities_cloud.py -p ${PART_OF_PAGE} -m ${NER_MODEL} -d ${YESTERDAY}

echo "Export entities to Big Query"
bq load --replace --source_format=NEWLINE_DELIMITED_JSON named_entities_raw.${PART_OF_PAGE} gs://cpto-content-metadata/content_ner/entities_${YESTERDAY}_${PART_OF_PAGE}.jsonl entities_bq_schema
