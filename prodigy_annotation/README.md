# Prodigy Annotation Environment

This repository folder has been created to ensure a seamless and portable annotation environment for annotators.
It follows a three-stage process:
1. Set up the environment
2. Build the environment using Docker
3. Begin annotation

#### Prerequisites

- A Prodigy access token saved in a `.secrets` file. Please talk to the project leads if you don't already have one.
- A prodigy `...db` database saved in `$HOME/.prodigy`

### 1. Setup Instructions

1. Download the Prodigy wheel file from https://$PRODIGY_LICENSE@download.prodi.gy where $PRODIGY_LICENSE is predefined in the repo .secrets file. Download the `prodigy-1.11.0-cp39-cp39-linux_x86_64.whl` wheel file and move it into the `wheel/` folder in the working directory.
2. Move the data you want to label into the `data/` folder in the working directory.


### 2. Build the Environment

1. Ensure you are in the `prodigy_annotation/` subdirectory.

2. Build the docker image, by running
    ```bash
    docker build -t prodann --no-cache .
    ```
    Or, if you are using and M1 machine
    ```bash
    docker build  --platform linux/amd64 -t prodann --no-cache .
    ```
    This builds a Docker image called `prodann` (prodigy annotation) locallly.

3. Run the docker image with
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

4. Run commands within the container by running

    ```bash
    docker exec -it prodann_con bash
    ```

    You will see your terminal change, and you will now be annotating in the Prodigy container environment.

### 3. Start Annotating

When in your containerised environment, you can run any prodigy commands as usual. For example:
```bash
prodigy ner.manual example_dataset en_core_web_md ./data/example_sentences.jsonl --label LABEL1,LABEL2,LABEL3
```
As the volume has been mounted between your host machine and the container in step 3, all databases will be saved in your local environment as well as the container.

A web server will start at `http://0.0.0.0:8080`

You should add your first initial and surname to the end of the webserver, so the annotation metadata is captured, for example:

`http://0.0.0.0:8080?session=rhurley`

or

`http://0.0.0.0:8080?session=atosi`
