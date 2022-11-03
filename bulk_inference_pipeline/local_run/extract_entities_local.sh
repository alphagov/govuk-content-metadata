#!/bin/bash

usage="Script to extract entities from pages on GOV.UK and stream output upload to Google Storage."

# The following options are available:
#  -m    full path to NER model to use for inference.  (Required)
#  -p    one of 'title', 'description', 'text' (Required)
#  -c    chunk size; number of texts to be streamed before memory is released (Optional)
#  -b    batch size; number of texts to be batched processed by the Spacy pipeline (Optional)
#  -n    number of cores for the parallel processing of texts (Optional)

# IMPORTANT: See the docstring in `bulk_inference_pipeline/local_run/extract_entities_local.py` for more details on
# which values to choose for the Optional arguments.

# Requirements:
# - Access to the Google Cloud Platform (GCP) project `cpto-content-metadata``
# - Ensure you meet all the `README.md/Inference pipeline [local machine]/Requirements`
# - This bash script must be run from the `bulk_inference_pipeline` sub-directory,
#       so please ensure you are in that directory:
#       % cd bulk_inference_pipeline

# The script consists of 4 steps:
# - Create input content data tables in Google Big Query
# - Run NER (bulk) inferential pipeline on your local machine
# - Stream uploading of results to a .jsonl file in Google Storage
# - Transfer the entities from Google Storage to Big Query tables

# Set default values for optional arguments
CHUNK_SIZE=5000
BATCH_SIZE=2000
N_PROC=1

# Set default value for `date` to yesterday in the format `DDMMYY`
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     YESTERDAY=$(date -d '-1 day' '+%d%m%y');;
    Darwin*)    YESTERDAY=$(date -v '-1d' '+%d%m%y');;
    *)          YESTERDAY="UNKNOWN:${unameOut}"
esac


while getopts ":m:p:c:b:n:" opt; do
    case $opt in
        m)
            echo "argument -m called with value $OPTARG" >&2
            NER_MODEL="${OPTARG}"
            ;;
        p)
            echo "argument -p called with value $OPTARG" >&2
            PART_OF_PAGE="${OPTARG}"
            ;;
        c)
            CHUNK_SIZE="${OPTARG}"
            echo "argument -c called with value $OPTARG" >&2
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
python -m src.create_input_files.py

echo "Running NER bulk inferential pipeline and streaming upload to Google Storage"
python -m local_run.extract_entities_local.py -p ${PART_OF_PAGE} -m ${NER_MODEL} -d ${YESTERDAY} -c ${CHUNK_SIZE} -b ${BATCH_SIZE} -n ${N_PROC}

echo "Export entities to Big Query"
bq load --replace --source_format=NEWLINE_DELIMITED_JSON named_entities_raw.${PART_OF_PAGE} gs://cpto-content-metadata/content_ner/entities_${YESTERDAY}_${PART_OF_PAGE}_*.jsonl src/infer_entities/entities_bq_schema
