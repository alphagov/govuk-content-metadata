## Prodigy Annotation Environment

This repository folder has been created to ensure a seamless and portable annotation environment for annotators.
It follows a three-stage process:
1. [Set up the environment](#1-setup-instructions)
2. [Build the environment using Docker](#2-build-the-environment)
3. [Begin annotation](#3-start-annotating)

In addition, once the annotation effort is completed:
4. [Review, compare and solve conflicts among the annotations of multiple annotators](#4-to-review-and-moderate-annotations-from-multiple-annotators)
5. [Export the annotations from Prodigy to a JSONL file](#5-export-annotations-to-a-jsonl-file).

### References

Please see Prodigy's official documentations at [prodi.gy/docs](https://prodi.gy/docs).

### Prerequisites

- A Prodigy access token saved in a `.secrets` file. Please talk to the project leads if you don't already have one.
- A prodigy `...db` database saved in `$HOME/.prodigy`


### 1. Setup Instructions

    1. Download the Prodigy wheel file from https://$PRODIGY_LICENSE@download.prodi.gy where $PRODIGY_LICENSE is predefined in the repo .secrets file. Download the `prodigy-1.11.8-cp39-cp39-linux_x86_64.whl` wheel file and move it into the `wheel/` folder in the working directory.

    2. Move the data you want to label into the [`data/` folder](/prodigy_annotation/data).

        Data must be in JSONL format, with each row containing the following fields:

        ```
        {"text": "Some text to be annotated",
        "meta": {
            "url": "https://www.gov.uk/something/something",
            ...
            }
        }
        ```

        You can specify any other "meta" subfields, for instance, we also used:
        - "line_number" (INT)
        - "regex_or_rand" ("regex" or "rand") to identify whether the text in the sample was picked via pattern matching or stratified random samplying
        - "cat" (STRING) to indicate the main entity category the text was identified for via pattern matching.

        Please refer to the following utility python modueles to create the JSONL file of texts to annotate:
        - [src/utils/csv_to_annotation.py](/src/utils/csv_to_annotation.py)
        - [src/utils/xls_to_match_patterns.py](/src/utils/xls_to_match_patterns.py)


### 2. Build the Environment

    1. Ensure you are in the `prodigy_annotation/` subdirectory.

    2. If necessary, update the [annotation_instructions.html](/prodigy_annotation/instructions/annotation_instructions.html) and the [prodigy.json](/prodigy_annotation/prodigy.json) with details about the entity schema to be annotated for.

    3. Build the docker image, by running

        ```bash
        docker build -t prodann --no-cache .
        ```

        Or, if you are using and M1 machine

        ```bash
        docker build  --platform linux/amd64 -t prodann --no-cache .
        ```

        This builds a Docker image called `prodann` (prodigy annotation) locallly.

    4. Run the docker image with

        ```bash
        docker run -itd --name prodann_con -p 8080:8080 -v $HOME/.prodigy:/app/.prodigy prodann
        ```

        or, if using and M1 machine

        ```bash
        docker run --platform linux/amd64 -itd --name prodann_con -p 8080:8080 -v $HOME/.prodigy:/app/.prodigy prodann
        ```

        This creates a container based on the docker image which will be the Prodigy annotation environment.
        The command is broken down as follows:

        * `docker run`: Run a docker container
        * `-it`,`d`: Run in _interactive_, _detached_ (background) mode
        * `--name prodann_con`: Name of the container
        * `-p 8080:8080`: Map port 8080 of the host (machine) to port 8080 of the container
        * `-v $HOME/.prodigy:/app/.prodigy`: Map the local .prodigy config to the location on the container. This is to persist data
        * `prodann`: The Docker image to use

        The container will start runnning in the backgrond.

    5. Run commands within the container by running

        ```bash
        docker exec -it prodann_con bash
        ```

        You will see your terminal change, and you will now be annotating in the Prodigy container environment.


### 3. Start Annotating

When in your containerised environment, you can run any prodigy commands as usual.

Please refer to Prodigy's documentation on [ner-manual](https://prodi.gy/docs/recipes#ner-manual), [ner-correct](https://prodi.gy/docs/recipes#ner-correct) and [https://prodi.gy/docs/recipes#ner-teach](ner-teach) for the different approaches to annotate, including pattern-matching and model-boostrapping functionalities.

For example:

```bash
prodigy ner.manual dataset_to_save_annotation blank:en data/examples_to_annotate.jsonl --label TITLE,ROLE,OCCUPATION,SECTOR,ORG,GPE,LOC,FAC --patterns data/phase_2_patterns_no_occ.jsonl
```

or

```bash
prodigy ner.correct dataset_to_save_annotation path/to/model-best data/examples_to_annotate.jsonl --label TITLE,ROLE,OCCUPATION,SECTOR,ORG,GPE,LOC,FAC --unsegmented
```

As the volume has been mounted between your host machine and the container in step 3, all databases will be saved in your local environment as well as the container.

A web server will start at `http://0.0.0.0:8080`

You should add your first initial and surname to the end of the webserver, so the annotation metadata is captured, for example:

`http://0.0.0.0:8080?session=rhurley`

or

`http://0.0.0.0:8080?session=atosi`


### 4. To review and moderate annotations from multiple annotators

```bash
prodigy review dataset_where_to_save_reviewed_anns dataset1_with_anns,dataset2_with_ann --label TITLE,ROLE,OCCUPATION,SECTOR,ORG,GPE,LOC,FAC --view-id ner_manual
```

### 5. Export annotations to a JSONL file

To export the annotations from a Prodigy dataset to a JSONL file, so that it can be used to train/fine-tune a model, execute:

```shell
prodigy db-out prodigy_annotation_dataset_to_be_exported > ./path/to/annotation_file.jsonl
```
