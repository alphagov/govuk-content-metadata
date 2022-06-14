<!-- SPACY PROJECT: AUTO-GENERATED DOCS START (do not remove) -->

# 🪐 spaCy Project: Content Metadata NER

A project for building a lanuage model for HM Governmentt

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
| `download` | Download the pretrained pipeline |
| `db-in` | Load data into prodigy |
| `data-to-spacy` | Merge annotations and create data in spaCy's binary format |
| `train_prodigy` | Train a named entity recognition model with Prodigy |
| `train_curve` | Train the model with Prodigy by using different portions of training examples to evaluate if more annotations can potentially improve the performance |

### ⏭ Workflows

The following workflows are defined by the project. They
can be executed using [`spacy project run [name]`](https://spacy.io/api/cli#project-run)
and will run the specified commands in order. Commands are only re-run if their
inputs have changed.

| Workflow | Steps |
| --- | --- |
| `all` | `download` &rarr; `db-in` &rarr; `data-to-spacy` &rarr; `train_prodigy` &rarr; `train_curve` |

### 🗂 Assets

The following assets are defined by the project. They can
be fetched by running [`spacy project assets`](https://spacy.io/api/cli#project-assets)
in the project directory.

| File | Source | Description |
| --- | --- | --- |
| [`assets/mark_goppepdm.jsonl`](assets/mark_goppepdm.jsonl) | Local | JSONL-formatted training data exported from Prodigy, annotated with `FASHION_BRAND` entities (1235 examples) |

<!-- SPACY PROJECT: AUTO-GENERATED DOCS END (do not remove) -->