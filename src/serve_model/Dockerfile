# python fastapi base
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim
# install requirements
RUN pip install --no-cache-dir spacy pydantic spacy-transformers
# copy all code
COPY main.py ./main.py
# copy model
COPY mdl_ner_trf_b1_b4 .
#command entrypoint
CMD uvicorn --host 0.0.0.0 main:app --port 8080
