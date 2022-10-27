FROM google/cloud-sdk:alpine as gcloud
WORKDIR /tmp
RUN mkdir models/
RUN gsutil -m cp -r gs://cpto-content-metadata/models/mdl_ner_trf_b1_b4 models/

FROM python:3.9-slim-buster
ENV PYTHONUNBUFFERED=1

WORKDIR /inference
# copy project
COPY . /inference/

# Copy relevant output from previous docker stage
RUN mkdir models/
COPY --from=gcloud tmp/models/. models/.

RUN pip install --upgrade pip
# install dependencies
RUN pip install -r requirements-inference-bulk.txt
# RUN apt-get update

COPY extract_entities_cloud.sh /usr/local/bin

# making executable file for bash shell (give bash permission to execute)
RUN chmod +x extract_entities_cloud.sh

ENTRYPOINT []

CMD ./extract_entities_cloud.sh -p "text" -m "models/model-best" | bash
