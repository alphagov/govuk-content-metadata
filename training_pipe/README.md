## Custom training of our NER models on Vertex AI

We trained (i.e., fine-tune) our NER models on Google Vertex AI, using a [custom container training workflow](https://cloud.google.com/vertex-ai/docs/training/overview#workflow_for_custom_training).

Our custom training application is built using [spaCy Projects](https://spacy.io/usage/projects) which simplifies the orchestration of the end-to-end fine-tuning workflow.

The training consists of two steps:

1. Preparing the training application
2. Creating and running a custom training job on Vertex AI

and additionally

3. Download the trained model and relevant files from the remote using [spacy project pull](https://spacy.io/api/cli#project-pull)


### 1. Preparing the training application

#### 1.1 Define a training workflow using SpaCy Projects

Our custom training application is built as a YAML file, called `project.yml`, using [spaCy Projects](https://spacy.io/usage/projects). A SpaCy Project streamlines the orchestration of the end-to-end fine-tuning workflow.

As we trained phase-1 and phase-2 models separately, we have created two separate training workflows, one for each entity phase. These can be found in [training_pipe/phase1_ner](/training_pipe/phase1_ner/) and [training_pipe/phase2_ner](/training_pipe/phase2_ner/), respectively.

- For more details on the workflows, refer to the `README.md` file and `project.yml` in each sub-directory.
- For an introduction to how spaCy projects work, refer to the official documentation [spaCy Projects](https://spacy.io/usage/projects).
- For an explanation of how to configure the training parameters, refer to [spaCy's guidelines on Training Config Systems](https://spacy.io/usage/training#config).
- We followed the recommended settings as highlighted in [spaCy's Training Quickstart](https://spacy.io/usage/training#quickstart) when selecting `Components: ner`, `Hardware: GPU (transformer)`, and `Optimize for: accuracy`. See also the [How are the config recommendations generated?](https://spacy.io/usage/training#quickstart-source) section.

In sum, for each phase, we fine-tuned the [roberta-base](https://huggingface.co/roberta-base) encoder-style transformer model on our custom labelled NER dataset.

The following hyperparameters were used during training:

- learning_rate: 0.00005
- optimizer: Adam with betas=(0.9,0.999) and epsilon=0.00000001
- patience: 1600 (the training will stop if there is no improvement in these many batches)
- max_steps: 20000 (the max number of iterations, each on one batch, to process)
- eval_frequency = 200 (batches)
- training.batcher.size = 2000 (size of each batch during training)
- nlp.batch_size = 128 (batch size during the evaluation steps, and the inference).

See these useful discussions: [spacy#8600](https://github.com/explosion/spaCy/discussions/8600), [spacy#7731](https://github.com/explosion/spaCy/discussions/7731) and [spacy#7465](https://github.com/explosion/spaCy/discussions/7465).


##### Updating or creating a new training workflow

In this section, we will refer to files in the `training_pipe/phase1_ner` workflow as an example. the same applies for `training_pipe/phase2_ner` or any new training pipeline to be set up.

1. Save your `data_train.jsonl` and `data_test.jsonl` in the [assets](training_pipe/phase1_ner/assets) folder. These files won't be version controlled.

    To ensure both the train and test dataset contain a fair representation of the distribution of all entity categories, use the utility python script [src/utils/stratify_train_test_split_entities.py](/src/utils/stratify_train_test_split_entities.py).

    These JSONL file are the exported version of a (combination of) Prodigy dataset(s), which, in turn, contains the output of Prodigy annotation sessions. See [prodigy_annotation](/prodigy_annotation/).

    Each line in these JSONL files has the following structure:
    ```
    {"text":"This is some text.",
    "meta":{"base_path":"/something/something",
            "doc_type":"a-govuk-document-type"},
    "_input_hash":INT,
    "_task_hash":INT,
    "tokens":[
        {"text":"This","start":INT,"end":INT,"id":INT,"ws":bool},
        {"text":"is","start":INT,"end":INT,"id":INT,"ws":bool},
        {}, ...],
    "spans":[
        {"token_start":INT,"token_end":INT,"start":INT,"end":INT,"text":STRING,"label":STRING}, {}, ...],
    "_is_binary":bool,
    "_view_id":STRING,
    "answer":STRING,
    "_timestamp":TIMESTAMP,
    "_annotator_id":STRING,
    "_session_id":STRING
    }
    ```

2. Update or create the [project.yaml](/training_pipe/phase1_ner/project.yml) file. In particular ensure the value of the `gcp_storage_remote` variable is the desired one; this is the location on Google Storage where the (hashed) fine-tuned model and releted files will be saved to when the Vertex AI pipeline is completed.

**IMPORTANT** SpaCy projects version control data, training config and outputs (i.e. model). To achieve this, as part of our spaCy training workflows, (the slate state of the) outputs are pushed to a remote Google Storage bucket, as specified in `project.yaml` using the [spacy project push](https://spacy.io/api/cli#project-push) functionality. Outputs are archived and compressed prior to upload, and addressed in the remote storage using the output’s relative path (URL encoded), a hash of its command string and dependencies, and a hash of its file contents. Please see [#3-download-the-trained-model-and-relevant-files-from-the-remote](#3-download-the-trained-model-and-relevant-files-from-the-remote) on how to retrieve and download these outputs once the Vertex AI training job has been completed.

#### 1.2 Create a custom container image

Once the training application has been set up (via `project.yaml`), create a custom Docker image and push it to Artifact Registry:

1. (optional) Update the [Dockerfile](/training_pipe/phase1_ner/Dockerfile)
2. (optional) Update the [cloudbuild.yaml](/training_pipe/phase1_ner/cloudbuild.yaml) by specifying a new docker image name
3. Build and push the docker image to Artifact Registry:
    ```shell
    cd training_pipe/phase1_ner
    gcloud builds submit --config cloudbuild.yaml .
    ```


### 2. Creating and running a custom training job on Vertex AI.

Refer to Vertex AI's official guidelines for custom training:
- [Workflow for custom training](https://cloud.google.com/vertex-ai/docs/training/overview#workflow_for_custom_training)
- [How training with containers works](https://cloud.google.com/vertex-ai/docs/training/containers-overview#how_training_with_containers_works)
- [Training: Create a custom job](https://cloud.google.com/vertex-ai/docs/training/create-custom-job#create)


##### Requirements

A user-generated service account, with the following permission:
- `storage.buckets.get` access to the Google Cloud Storage bucket gs://cpto-content-metadata


#### 2.1 Configure and create the training job

Select the compute resources to run the training job. These have been our settings so far:

```
LOCATION=europe-west2
MACHINE_TYPE=n1-standard-8
ACCELERATOR_TYPE=NVIDIA_TESLA_T4
REPLICA_COUNT=1
```

##### Using Google Cloud console

Follow these steps, after clicking on the `console` tab: [create-custom-job#create](https://cloud.google.com/vertex-ai/docs/training/create-custom-job#create).

Once in Vertex AI Create New Train Model panel, select:

- `Dataset`: "No managed dataset"
- `Model training method`: "Custom training (advanced)"
- `Model details`: "Train new model"
- `Name`: specify a name for the traininig job
- `Description`: specify a description for the traininig job
- `Service account`: select the `NER_VERTEX_TRAINING_SA` service account
- `Training container`: "Custom container"
- `Container image`: specify the Artifact Registry URI of your container image
- `Model output directory`: leave blank
- `Hyperparameter tuning`: unselect
- `Compute and pricing - Region`: "europe-west2"
- `Compute and pricing - Worker pool 0 - Machine type`: "n1-standard-8"
- `Compute and pricing - Worker pool 0 - Accelerator type`: "NVIDIA_TESLA_T4"
- `Compute and pricing - Worker pool 0 - Accelerator count`: 1
- `Compute and pricing - Worker pool 0 - Worker count`: 1
- `Prediction container`: "No prediction container"

Click on `START TRAINING`.


### 3. Download the trained model and relevant files from the remote

We use [spacy project pull](https://spacy.io/api/cli#project-pull) to retrieve the training outputs, most importantly the fine-tuned NER model, and download it to our local machines. Refer to the official guidelines on how this works (previous link) and this [explosion/spaCy/discussion](https://github.com/explosion/spaCy/discussions/12238).
