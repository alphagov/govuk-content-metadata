FROM nvidia/cuda:11.7.0-runtime-ubuntu20.04

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
    && python3.9 -m pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "python3.9" ]
CMD ["-m", "spacy", "project", "run", "all"]
