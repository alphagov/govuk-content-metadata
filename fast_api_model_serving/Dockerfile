# python fastapi base
# ref: https://fastapi.tiangolo.com/deployment/docker/#official-docker-image-with-gunicorn-uvicorn
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim
# install requirements
RUN pip install --no-cache-dir spacy>=3.5.0 pydantic>=1.10.4 spacy-transformers>=1.2.2
# copy all code
COPY main.py ./main.py
# copy models
COPY ./models ./models
RUN ls --recursive .
#command entrypoint
CMD uvicorn --host 0.0.0.0 main:app --port 8080
