FROM nvidia/cuda:11.2.1-runtime-ubuntu20.04

WORKDIR /train
ENV PYTHONUNBUFFERED=1

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/London
RUN apt update && apt-get install -y apt-transport-https && \
    apt install --no-install-recommends -y build-essential software-properties-common && \
    add-apt-repository -y universe && \
    apt install --no-install-recommends -y python3.9 python3-pip python3-setuptools python3-distutils && \
    apt clean && rm -rf /var/lib/apt/lists/*

COPY . .

RUN ls --recursive .

RUN python3.9 -m pip install --upgrade pip \
    && python3.9 -m pip install prodigy-1.11.8-cp39-cp39-linux_x86_64.whl \
    && python3.9 -m pip install -U setuptools wheel \
    && python3.9 -m pip install 'spacy[cuda112,transformers]' \
    && rm -rf prodigy-1.11.8-cp39-cp39-linux_x86_64.whl

# RUN python3.9 -m pip3.9 install --no-cache-dir -r requirements.txt


ENTRYPOINT [ "python3" ]
CMD ["-m", "spacy", "project", "run", "all"]
