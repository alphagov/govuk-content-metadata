# python fastapi base
# ref: https://fastapi.tiangolo.com/deployment/docker/#official-docker-image-with-gunicorn-uvicorn
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim
# install requirements
RUN pip install --no-cache-dir spacy pydantic spacy-transformers
# copy all code
COPY main.py ./main.py
# copy models
COPY ./models ./models
RUN ls --recursive .
#command entrypoint
CMD uvicorn --host 0.0.0.0 main:app --port 8080
