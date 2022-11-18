FROM python:3.9-slim-buster as python-img
ENV PYTHONUNBUFFERED=1

WORKDIR /inference
# copy project

# install dependencies
COPY requirements-inference-bulk.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Downlaod gcloud
RUN apt-get update && apt-get install -y curl && curl -sSL https://sdk.cloud.google.com | bash
# Adding the package path to local
ENV PATH=$PATH:/root/google-cloud-sdk/bin

COPY . .
# RUN mkdir models/
# RUN gsutil -m cp -r gs://cpto-content-metadata/models/mdl_ner_trf_b1_b4/model-best models/
RUN ls --recursive .

# COPY extract_entities_cloud.sh .
# making executable file for bash shell (give bash permission to execute)
RUN chmod +x extract_entities_cloud.sh

ENTRYPOINT []

CMD bash ./extract_entities_cloud.sh -m "./models/model-best" -b 4000 -n 12
