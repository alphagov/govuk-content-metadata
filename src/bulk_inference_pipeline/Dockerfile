FROM google/cloud-sdk:alpine as gcloud
WORKDIR /tmp
RUN mkdir models/
RUN gsutil -m cp -r gs://cpto-content-metadata/models/mdl_ner_trf_b1_b4 models/

FROM python:3.9-slim-buster as python-img
ENV PYTHONUNBUFFERED=1
RUN echo "created python env"

WORKDIR /inference
# copy project
COPY . /inference/
RUN echo "copied workdir to docker workdir"

# Copy relevant output from previous docker stage
RUN mkdir models/
COPY --from=gcloud tmp/models/. models/.
RUN echo "copied downloaded model over"

RUN pip install --upgrade pip
# install dependencies
RUN pip install -r requirements-inference-bulk.txt
# RUN apt-get update

# Downlaod gcloud
RUN apt-get update && apt-get install -y curl && curl -sSL https://sdk.cloud.google.com | bash
# Adding the package path to local
# ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin
ENV PATH=$PATH:/root/google-cloud-sdk/bin

COPY extract_entities_cloud.sh /usr/local/bin
RUN echo "ran COPY extract_entities_cloud.sh /usr/local/bin"

# making executable file for bash shell (give bash permission to execute)
RUN chmod +x extract_entities_cloud.sh

ENTRYPOINT []

CMD ./extract_entities_cloud.sh -p "text" -m "models/model-best" | bash
RUN echo "ran CMD ./extract_entities_cloud.sh ... |bash"
