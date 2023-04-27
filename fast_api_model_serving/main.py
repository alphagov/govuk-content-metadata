# This script is a FastAPI app which is intended to serve NER predictions from a model via HTTP calls.
# For more information on the conventions used, visit https://fastapi.tiangolo.com/tutorial/first-steps/
# for comprehensive explainations.

# To run locally for quick testing:
# uvicorn main:app --reload
# http://localhost:8000/docs

from typing import Union, Any
from fastapi import FastAPI
import spacy
from pydantic import BaseModel, HttpUrl, Field
from src.model_helpers import combine_ner_components

# Metadata
tags_metadata = [
    {
        "name": "ner",
        "description": "Extract named entities from one document",
    },
    {
        "name": "ner-vertex-ai",
        "description": "Extract named entities from multiple documents",
    },
]

# Initialisation - create a FastAPI instance
app = FastAPI(
    title="GovNER API",
    description="Extracting named entities from GOV.UK using a custom NER spacy model",
    openapi_tags=tags_metadata,
)

print("Load the spacy models")
nlp_phase1 = spacy.load("models/phase1_ner_trf_model/model-best")
nlp_phase2 = spacy.load("models/phase2_ner_trf_model/model-best")

nlp = combine_ner_components(nlp_phase1, nlp_phase2)

# Request Bodies - Data Model class


class InputContent(BaseModel):
    """
    Data model for the body prediction request.
    """

    url: Union[HttpUrl, None] = Field(
        default=None,
        description="Valid URL of the webpage from which the text is taken.",
    )
    text: str = Field(
        description="String of text to feed to the model to extract entities."
    )
    line_number: Union[int, None] = Field(
        default=None, description="Line number of the text on the webpage"
    )
    part_of_page: Union[str, None] = Field(
        default=None, description="Part of page (e.g., 'title')"
    )

    class Config:
        schema_extra = {
            "example": {
                "url": "https://www.gov.uk/government/people/rishi-sunak",
                "text": "Rishi Sunak became Prime Minister on 25 October 2022",
                "line_number": 2,
                "part_of_page": "title",
            }
        }


class InputContentVertexAI(BaseModel):
    """
    JSON body format of prediction requests for Vertex AI.
    Ref: https://cloud.google.com/vertex-ai/docs/predictions/custom-container-requirements
    """

    instances: list[InputContent]


# Response Data Models


class SingleEntity(BaseModel):
    """
    Basic response data model: returns the entities, their type and their locations.
    """

    name: str = Field(description="Name/text of the extracted entity instance.")
    type: str = Field(
        description="The entity type with which the entity name was tagged."
    )
    start: int = Field(
        ge=0, description="The index of the first token of the entity name."
    )
    end: int = Field(description="The index of the last token of the entity name.")

    class Config:
        schema_extra = {
            "example": {
                "name": "25 October 2022",
                "type": "DATE",
                "start": 37,
                "end": 52,
            }
        }


class OutputEntities(BaseModel):
    """
    Response data model for a single document input: structure of responses that will be sent back by the server.
    """

    url: Union[HttpUrl, None] = Field(
        default=None,
        description="Valid URL of the webpage from which the text is taken.",
    )
    entities: list[SingleEntity]
    line_number: Union[int, None] = Field(
        default=None, description="Line number of the text on the webpage"
    )
    part_of_page: Union[str, None] = Field(
        default=None, description="Part of page (e.g., 'title')"
    )

    class Config:
        schema_extra = {
            "example": {
                "url": "https://www.gov.uk/government/people/rishi-sunak",
                "entities": [
                    {"name": "Rishi Sunak", "type": "PERSON", "start": 0, "end": 11},
                    {"name": "Prime Minister", "type": "TITLE", "start": 19, "end": 33},
                    {"name": "25 October 2022", "type": "DATE", "start": 37, "end": 52},
                ],
                "line_number": 2,
                "part_of_page": "text",
            }
        }


class ResponseEntitiesVertexAI(BaseModel):
    """
    JSON body format of prediction response for Vertex AI.
    Response data model for multiple documents.
    Ref: https://cloud.google.com/vertex-ai/docs/predictions/custom-container-requirements
    """

    predictions: list[OutputEntities]


# Request paths
# GET endpoint for app root
@app.get("/")
async def root():
    return {"message": "Hello World!"}


# GET endpoint for app health check to ensure server is running
@app.get("/health-check", status_code=200)
async def health_check():
    return {"response": "HTTP 200 OK"}


# POST endpoints for predictions


@app.post("/ner", tags=["ner"], response_model=OutputEntities)
async def get_entities_one_doc(input: InputContent) -> Any:
    document = nlp(input.text)
    entities = [
        {
            "name": ent.text,
            "type": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char,
        }
        for ent in document.ents
    ]
    return {
        "url": input.url,
        "entities": entities,
        "line_number": input.line_number,
        "part_of_page": input.part_of_page,
    }


@app.post(
    "/ner-vertex-ai", tags=["ner-vertex-ai"], response_model=ResponseEntitiesVertexAI
)
async def get_entities(input: InputContentVertexAI) -> Any:
    documents = [nlp(instance.text) for instance in input.instances]
    entities = [
        [
            {
                "name": ent.text,
                "type": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            }
            for ent in document.ents
        ]
        for document in documents
    ]
    return {
        "predictions": [
            {
                "url": instance.url,
                "entities": ents,
                "line_number": instance.line_number,
                "part_of_page": instance.part_of_page,
            }
            for instance, ents in zip(input.instances, entities)
        ]
    }
