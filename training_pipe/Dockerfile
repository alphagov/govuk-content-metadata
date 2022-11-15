FROM python:3.9-slim-buster as python-img
ENV PYTHONUNBUFFERED=1

WORKDIR /train

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# CMD python -m spacy train phase_1_corpus/config.cfg --output ./phase_1_output --paths.train ./phase_1_corpus/train.spacy --paths.dev ./phase_1_corpus/dev.spacy

ENTRYPOINT ["python3", "train.py"]
