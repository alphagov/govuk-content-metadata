# :mag: GovNER :monocle_face: : extracting Named Entities from GOV.UK

Repository for the GovNER project.

GovNER systematically extracts key metadata from the content of the GOV.UK website. GovNER is an encoder-based language model (RoBERTa) that has been fine-tuned to perform Named Entity Recognition (NER) on "govspeak", the language(s) specific of the GOV.UK content estate.

The repository consists of 5 main stand-alone components, each contained in their own sub-directory:

- [Daily NER inference pipeline](#daily-new-content-only-inference-pipeline)
- [Bulk NER inference pipeline](#bulk-inference-pipeline)
- [Model fine-tuning pipeline](#training-pipeline)
- [Model serving via REST API](#serving-the-model-in-production-via-fastapi-and-uvicorn)
- [GovNER web app](#govner-web-app)


## Tech Stack :cherries:

* Python
* FastApi / uvicorn
* Docker
* Google Cloud Platform  (Cloud Engine, Vertex AI, Workflows, Cloud Run, BigQuery, Storage,  Scheduler)
* Github Actions
* bash


## Named Entity Recognition (NER) and Entity Schema

Named Entity Recognition (NER) is an Natural Language Processing (NLP) technique, a type of multi-class supervised machine-learning method that identifies and sorts 'entities', real-world things like people, organisations or events, from text.

The Named Entity Schema is the set of all entity types (i.e., categories) that the NER model is trained to extract, together with their definitions and annotation instructions. For GovNER, we built as much as possible on [schema.org](https://schema.org/). Using an agile approach, delivery was broken down into 3 phases, corresponding to three sets of entity types, for which we fine-tuned separate NER models. We have so far completed 2 phases. Predictions from these models were combined at inference stage.

#### Phase-1 entities

- Money (amount)
- Form (government forms)
- Person
- Date
- Postcode
- Email
- Phone (number)

#### Phase-2 entities

- Occupation
- Role
- Title
- GPE
- Location (non-GPE)
- Facility
- Organisation
- Event


## Daily 'new content only' inference pipeline :rocket:

Complete code, requirements and documentation in [inference_pipeline_new_content](/bulk_inference_pipeline).

Inference pipeline scheduled to run daily to extract named entities from the content items on GOV.UK that substantially changed or were newly created the day before.

Vertex AI Batch Predictions are served via HTTP POST method, as part of a scheduled Google Cloud Workflow.

## Serving the model in production via FastAPI and uvicorn :unicorn:

Complete code, requirements and documentation in [fast_api_model_serving](/fast_api_model_serving).

Containerised code to deploy and run an HTTP server to serve predictions vis API for our custom-trained fine-tuned NER models.


## Bulk inference pipeline :weight_lifting:

Complete code, requirements and documentation in [bulk_inference_pipeline](/bulk_inference_pipeline).

Inference pipeline to extract named entities from the whole GOV.UK content estate (in "bulk").
The pipeline is deployed in a Docker container onto a Virtual Machine (VM) instance with GPU on Google Compute Engine (GCE).

The bulk pipeline is intended to be executed as a one-off, if either of the phase-1 entity or phase-2 entity models is retrained and re-deployed.


## Training pipeline :running:

Complete code, requirements and documentation in [training_pipe](/training_pipe).

Pipeline to fine-tune the encoder-style transformer `roberta-base` for custom NER on Google Vertex AI, using a [custom container training workflow](https://cloud.google.com/vertex-ai/docs/training/overview#workflow_for_custom_training) and [spaCy Projects](https://spacy.io/usage/projects) for the training application.


### Annotation workflow :pencil:

Complete code, requirements and documentation in [prodigy_annotation](/prodigy_annotation).

Containerised code to create an annotation environment for annotators, using the proprietary software Prodigy.


## GovNER web app :computer:

Complete code, requirements and documentation in [src/ner_streamlit_app](/src/ner_streamlit_app).

Containerised code to build the interactive web application aimed at helping prospective users understand how NER works via visualisation and user interaction.


## Developing :building_construction:

```{warning}
Where we refer to the root directory we mean where this README.md is located.
```

### Requirements :construction:

- Git
- [pre-commit](https://pre-commit.com/)
- [Make](https://formulae.brew.sh/formula/make)
- [gcloud CLI](https://cloud.google.com/sdk/gcloud)
- [Docker](https://www.docker.com/)
- Python (v3.9+) - Only for local development without Docker

In addition:

- a `.secrets` file in this repository's root directory
- [loaded environment variables](/docs/user_guide/loading_environment_variables.md) from `.envrc`

#### Credentials

Access to the project on Google Cloud Platform.


#### Python requirements and pre-commit hooks

To install the Python requirements and pre-commit hooks, open your terminal and enter:

```shell
make requirements
```

or, alternatively, to only install the necessary Python packages using pip:

```shell
pip install -r requirements.txt
```

To add to the Python requirement file, add any new dependencies actually imported in your code to the `requirements-original.txt` file, and then run:

```shell
pip freeze -r requirements-original.txt > requirements.txt
```

### Tests :vertical_traffic_light:

Tests are run as part of [a GitHub action](/.github/workflows/ci.yml).

To run test locally:

```shell
pytest
```

## Licence

Unless stated otherwise, the codebase is released under the MIT License. This covers
both the codebase and any sample code in the documentation. The documentation is ©
Crown copyright and available under the terms of the Open Government 3.0 licence.
