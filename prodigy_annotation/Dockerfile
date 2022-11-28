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

ENV PRODIGY_HOME /app
ENV PRODIGY_LOGGING "verbose"
ENV PRODIGY_ALLOWED_SESSIONS "user1,user2"
ENV PRODIGY_BASIC_AUTH_USER "admin"
ENV PRODIGY_BASIC_AUTH_PASS "password"

EXPOSE 8080

# CMD python -m prodigy ner.manual ner_news en_core_web_md ./data/news_headlines.jsonl --label PERSON,ORG,PRODUCT
# docker run -it -p 8080:8080 prodigy bash
# CMD docker run -it -p 9001:8080 -v "$(pwd):work" prodigy bash
# docker run -it -p 8080:8080 -v "$(pwd):$(pwd)" prodigy bash
