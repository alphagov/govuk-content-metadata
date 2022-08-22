#!/bin/bash

usage="Script to extract entities from pages on GOV.UK and upload outputs to S3."

# The following options are available:
#  -m    full path to NER model to use for inference.  (Required)
#  -p    one of 'title', 'description', 'text' (Required)
#  -d    date 'YYYY-MM-DD' of the preprocessed content store copy (Optional)
#  -c    chunk size; number of texts to be streamed before memory is released (Optional)
#  -b    batch size; number of texts to be batched processed by the Spacy pipeline (Optional)
#  -n    number of cores for the parallel processing of texts (Optional)

# IMPORTANT: See the docstring in `src/make_data/infer_entities.py` for more details.

# The script consists of 3 steps:
# - Downlowding copy of preprocessed content store from AWS S3
# - Running NER inferential pipeline
# - Uploading files with extracted entities to AWS S3

# Set default values for optional arguments
DATE=$(date -v-1d +%F)
CHUNK_SIZE=40000
BATCH_SIZE=30
N_PROC=1

# echo ${DATE_YESTERDAY}
# echo ${CHUNK_SIZE}

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

echo "Downlowding copy of preprocessed content store from AWS S3"
python3 -m src.make_data.get_preproc_content --date ${DATE}

echo "Running NER inferential pipeline"
python3 -m src.make_data.infer_entities -p ${PART_OF_PAGE} -m ${NER_MODEL} -d ${DATE} -c ${CHUNK_SIZE} -b ${BATCH_SIZE} -n ${N_PROC}

echo "Uploading files with extracted entities to AWS S3"
python3 -m src/make_data/upload_entities_to_s3
