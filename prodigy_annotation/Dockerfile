FROM python:3.9-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY wheel/prodigy-1.11.0-cp39-cp39-linux_x86_64.whl ./wheel/
RUN pip install wheel/prodigy-1.11.0-cp39-cp39-linux_x86_64.whl \
    && rm -rf wheel/prodigy-1.11.0-cp39-cp39-linux_x86_64.whl
RUN spacy download en_core_web_md

COPY prodigy.json .
COPY data ./data/
COPY instructions ./instructions/

# environment variable to set the prodigy home directory and track annotation sessions
# see https://prodi.gy/docs/install#env-variables for more info
ENV PRODIGY_HOME /app/.prodigy

ENV PRODIGY_ALLOWED_SESSIONS "atosi,rhurley"

EXPOSE 8080

CMD bash
