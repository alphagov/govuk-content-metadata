# FROM google/cloud-sdk:alpine as gcloud
# WORKDIR /tmp
# RUN mkdir models/
# RUN gsutil -m cp -r gs://cpto-content-metadata/models/mdl_ner_trf_b1_b4 models/

FROM python:3.9-slim-buster as python-img
ENV PYTHONUNBUFFERED=1

WORKDIR /inference
# copy project
COPY . /inference/

# Copy relevant output from previous docker stage
# RUN mkdir models/
# COPY --from=gcloud tmp/models/. models/.
# RUN echo "copied downloaded model over"

# Downlaod gcloud
# See bullet 3) Docker-tip at https://cloud.google.com/sdk/docs/install#deb
RUN apt-get update && apt-get install -y curl && curl -sSL https://sdk.cloud.google.com | bash
# Adding the package path to local
ENV PATH=$PATH:/root/google-cloud-sdk/bin

# RUN apt-get update -y && apt-get install -y apt-utils 2>&1 && apt-get install -y curl apt-transport-https ca-certificates gnupg
# RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" \
#    | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
#    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg \
#    | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - \
#    && apt-get update -y && apt-get install google-cloud-cli -y

RUN pip install --upgrade pip
# install dependencies
RUN pip install -r requirements-inference-bulk.txt
# RUN apt-get update

RUN mkdir models/
RUN gsutil -m cp -r gs://cpto-content-metadata/models/mdl_ner_trf_b1_b4/model-best models/
RUN ls --recursive /inference/

COPY extract_entities_cloud.sh .
# making executable file for bash shell (give bash permission to execute)
RUN chmod +x extract_entities_cloud.sh

ENTRYPOINT []

CMD bash ./extract_entities_cloud.sh -p "text" -m "/inference/models/model-best"
