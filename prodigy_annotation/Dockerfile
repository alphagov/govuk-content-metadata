FROM python:3.9-slim

COPY requirements.txt /app/
WORKDIR /app

RUN pip install --upgrade pip \
    && pip install --trusted-host pypi.python.org -r requirements.txt

COPY wheel/prodigy-1.11.0-cp39-cp39-linux_x86_64.whl ./wheel/
RUN pip install wheel/prodigy-1.11.0-cp39-cp39-linux_x86_64.whl \
    && rm -rf wheel/prodigy-1.11.0-cp39-cp39-linux_x86_64.whl
RUN python -m spacy download en_core_web_md

COPY prodigy.json .
COPY data ./data/
COPY instructions ./instructions/

ENV PRODIGY_HOME /app/.prodigy
ENV PRODIGY_ALLOWED_SESSIONS "atosi,rhurley"

EXPOSE 8080

CMD bash

# docker run -itd --name prodann_con -p 8080:8080 -v /Users/roryhurley/.prodigy:/app/.prodigy prodann

# docker exec -it prodann_con bash
