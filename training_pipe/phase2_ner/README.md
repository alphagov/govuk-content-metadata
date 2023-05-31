<!-- SPACY PROJECT: AUTO-GENERATED DOCS START (do not remove) -->

# 🪐 spaCy Project: GovNER Phase2 SpaCy Training Pipeline

SpaCy pipeline to train NER model for phase-2 entities. Runs through multiple stages including data prep and training

## 📋 project.yml

The [`project.yml`](project.yml) defines the data assets required by the
project, as well as the available commands and workflows. For details, see the
[spaCy projects documentation](https://spacy.io/usage/projects).

### ⏯ Commands

The following commands are defined by the project. They
can be executed using [`spacy project run [name]`](https://spacy.io/api/cli#project-run).
Commands are only re-run if their inputs have changed.

| Command | Description |
| --- | --- |
| `get-assets` | Fetch project assets |
| `preprocess` | Convert the data to spaCy's binary format |
| `create-config` | Initialise and save a config.cfg file using the recommended settings for your use case |
| `train_spacy` | Train a named entity recognition model with spaCy |
| `evaluate` | Evaluate the model and export metrics |
| `push_remote` | Push outputs to remote |
| `clean` | Remove intermediate files |

### ⏭ Workflows

The following workflows are defined by the project. They
can be executed using [`spacy project run [name]`](https://spacy.io/api/cli#project-run)
and will run the specified commands in order. Commands are only re-run if their
inputs have changed.

| Workflow | Steps |
| --- | --- |
| `all` | `get-assets` &rarr; `preprocess` &rarr; `create-config` &rarr; `train_spacy` &rarr; `evaluate` &rarr; `push_remote` |

### 🗂 Assets

The following assets are defined by the project. They can
be fetched by running [`spacy project assets`](https://spacy.io/api/cli#project-assets)
in the project directory.

| File | Source | Description |
| --- | --- | --- |
| [`assets/data_train.jsonl`](assets/data_train.jsonl) | Local | JSONL-formatted training data exported from Prodigy |
| [`assets/data_test.jsonl`](assets/data_test.jsonl) | Local | JSONL-formatted development data exported from Prodigy |

<!-- SPACY PROJECT: AUTO-GENERATED DOCS END (do not remove) -->
