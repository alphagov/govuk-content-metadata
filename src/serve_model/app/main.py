from fastapi import FastAPI
from typing import List
import spacy
from pydantic import BaseModel
from google.cloud import storage
from .download_models import replicate_folder_structure, download_files_from_bucket


app = FastAPI()


def load_model(model_path):
    """Load Transformer model.

    :param model_path: Path to Transformer model.
    :type model_path: str
    :return: Transformer pipeline.
    :rtype: Model.
    """

    # instantiate_storage_client
    storage_client = storage.Client()
    bucket_name = "cpto-content-metadata"

    replicate_folder_structure(
        bucket_name=bucket_name,
        folder="models/mdl_ner_trf_b1_b4/model-best",
        storage_client=storage_client,
    )
    download_files_from_bucket(
        bucket_name=bucket_name,
        folder="models/mdl_ner_trf_b1_b4/model-best",
        storage_client=storage_client,
    )
    nlp = spacy.load(model_path)
    return nlp


nlp = load_model(model_path="models/mdl_ner_trf_b1_b4/model-best")


class Content(BaseModel):
    post_url: str
    content: str


class Payload(BaseModel):
    instances: List[Content]


class SingleEntity(BaseModel):
    text: str
    entity_type: str


class Entities(BaseModel):
    post_url: str
    entities: List[SingleEntity]


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health_check", status_code=200)
async def health_check():
    return {"response": "HTTP 200 OK"}


@app.get("/multiply_by_four/{num}")
async def multiply_by_four(num: int):
    out_num = num * 4
    return {"message": f"{num} multiplied by 4 is {out_num}"}


@app.post("/ner-service")
async def get_ner(payload: Payload):
    tokenize_content: List[spacy.tokens.doc.Doc] = [
        nlp(content.content) for content in payload.instances
    ]
    document_enities = []
    for doc in tokenize_content:
        document_enities.append(
            [{"text": ent.text, "entity_type": ent.label_} for ent in doc.ents]
        )
    return {
        "predictions": [
            Entities(post_url=post.post_url, entities=ents)
            for post, ents in zip(payload.instances, document_enities)
        ]
    }
