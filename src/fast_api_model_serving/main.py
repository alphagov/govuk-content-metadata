# This script is a FastAPI app which is intended to serve NER predictions from a model via HTTP calls.
# For more information on the conventions used, please visit https://fastapi.tiangolo.com/tutorial/first-steps/
# for comprehensive explainations.

from fastapi import FastAPI
from typing import List
import spacy
from pydantic import BaseModel

# Initialisation
# create a FastAPI instance
app = FastAPI()

# load the spacy model
nlp = spacy.load("model-best")


# Model classes
# create a data model for requested url-content key-value pairs
class Content(BaseModel):
    post_url: str
    content: str


# create a data model for lists of Content model types
class Payload(BaseModel):
    instances: List[Content]


# create a data model for responses of text-entity key-value pairs
class SingleEntity(BaseModel):
    text: str
    entity_type: str


# create a model for for lists of Single Entity key-value pairs
class Entities(BaseModel):
    post_url: str
    entities: List[SingleEntity]


# Request paths
# get path for app root
@app.get("/")
async def root():
    return {"message": "Hello World"}


# get path for app health check to ensure server is running
@app.get("/health_check", status_code=200)
async def health_check():
    return {"response": "HTTP 200 OK"}


# post path for getting ner predictions
@app.post("/ner-service")
async def get_ner(payload: Payload):
    tokenize_content: List[spacy.tokens.doc.Doc] = [
        nlp(content.content) for content in payload.instances
    ]
    document_enities = []
    for doc in tokenize_content:
        # GCP Vertex AI expects custom model payload to be a list of dicts [{'...':'...'}, {'...':'...'}, ...]
        document_enities.append(
            [{"text": ent.text, "entity_type": ent.label_} for ent in doc.ents]
        )
    # GCP Vertex AI expects custom models to return response {"predictions": [... , ...]}
    return {
        "predictions": [
            Entities(post_url=post.post_url, entities=ents)
            for post, ents in zip(payload.instances, document_enities)
        ]
    }
