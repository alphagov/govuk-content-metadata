<!-- SPACY PROJECT: AUTO-GENERATED DOCS START (do not remove) -->

# spaCy Project: GovNER SpaCy Training Pipeline

SpaCy pipeline to train NER model. Runs through multiple stages including data prep and training

## project.yml

The [`project.yml`](project.yml) defines the data assets required by the
project, as well as the available commands and workflows. For details, see the
[spaCy projects documentation](https://spacy.io/usage/projects).

### Commands

The following commands are defined by the project. They
can be executed using [`spacy project run [name]`](https://spacy.io/api/cli#project-run).
Commands are only re-run if their inputs have changed.

| Command | Description |
| --- | --- |
| `db-in` | Load the annotated .jsonl file in as a prodigy database. |
| `data-to-spacy` | Convert labelled data to spaCy's binary format |
| `train_spacy` | Train a named entity recognition model with spaCy |
| `push_remote` | Push outputs to remote |
| `clean` | Remove intermediate files |

### Workflows

The following workflows are defined by the project. They
can be executed using [`spacy project run [name]`](https://spacy.io/api/cli#project-run)
and will run the specified commands in order. Commands are only re-run if their
inputs have changed.

| Workflow | Steps |
| --- | --- |
| `all` | `db-in` &rarr; `data-to-spacy` &rarr; `train_spacy` &rarr; `push_remote` |

### Assets

The following assets are defined by the project. They can
be fetched by running [`spacy project assets`](https://spacy.io/api/cli#project-assets)
in the project directory.

| File | Source | Description |
| --- | --- | --- |
| `assets/phase_1_annotations.jsonl` | URL | JSONL-formatted training data exported from Prodigy |

<!-- SPACY PROJECT: AUTO-GENERATED DOCS END (do not remove) -->
