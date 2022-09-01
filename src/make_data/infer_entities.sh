#!/bin/bash

usage="Script to extract entities from pages on GOV.UK and upload outputs to S3."

# The following options are available:
#  -m    full path to NER model to use for inference.  (Required)
#  -p    one of 'title', 'description', 'text' (Required)
#  -d    date 'DDMMYY' of the preprocessed content store copy (Optional)
#  -c    chunk size; number of texts to be streamed before memory is released (Optional)
#  -b    batch size; number of texts to be batched processed by the Spacy pipeline (Optional)
#  -n    number of cores for the parallel processing of texts (Optional)

# IMPORTANT: See the docstring in `src/make_data/infer_entities.py` for more details on
# which values to choose for the Optional arguments.

# Requirements:
# - Ensure you meet all the `README.md/Inference pipeline [local machine]/Requirements`.

# The script consists of 3 steps:
# - Downlowding copy of the preprocessed content store from AWS S3
# - Running NER inferential pipeline
# - Uploading files with extracted entities to AWS S3

# Set default values for optional arguments
CHUNK_SIZE=40000
BATCH_SIZE=30
N_PROC=1

S3_BUCKET=govuk-data-infrastructure-integration
LOCAL_FOLDER_CONTENT=data/raw
LOCAL_FOLDER_ENTITIES=data/processed/entities

# Set default value for `date` to yesterday in the format `DDMMYY`
unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     DATE=$(date -d '-1 day' '+%d%m%y');;
    Darwin*)    DATE=$(date -v '-1d' '+%d%m%y');;
    *)          DATE="UNKNOWN:${unameOut}"
esac


while getopts ":m:p:d:c:b:n:" opt; do
    case $opt in
        m)
            echo "argument -m called with value $OPTARG" >&2
            NER_MODEL="${OPTARG}"
            ;;
        p)
            echo "argument -p called with value $OPTARG" >&2
            PART_OF_PAGE="${OPTARG}"
            ;;
        d)
            DATE="${OPTARG}"
            echo "argument -d called with value $DATE" >&2
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


# date in YYYY-MM-DD format
DATE_LONG=20${DATE:(-2)}-${DATE:2:2}-${DATE:0:2}
echo "Selected date: ${DATE_LONG}"

echo "Getting copy of preprocessed content store from AWS S3"
FILE=${LOCAL_FOLDER_CONTENT}/preprocessed_content_store_${DATE}.csv.gz
if [ -f "${FILE}" ]; then
    echo "File ${FILE} already downloaded."
else
    echo "Downloading ${FILE}..."
	aws s3 cp s3://${S3_BUCKET}/knowledge-graph/${DATE_LONG}/preprocessed_content_store_${DATE}.csv.gz ${LOCAL_FOLDER_CONTENT}/preprocessed_content_store_${DATE}.csv.gz --profile govuk-datascience
    echo "Successfully downloaded ${FILE}."
fi

echo "Running NER inferential pipeline"
python3 -m src.make_data.infer_entities -p ${PART_OF_PAGE} -m ${NER_MODEL} -d ${DATE_LONG} -c ${CHUNK_SIZE} -b ${BATCH_SIZE} -n ${N_PROC}

echo "Uploading files with extracted entities to AWS S3"
aws s3 cp ${LOCAL_FOLDER_ENTITIES} s3://${S3_BUCKET}/knowledge-graph-static/entities_intermediate/ --recursive --exclude "*" --include "*.jsonl" --profile govuk-datascience
