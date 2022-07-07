# `configs` folder overview

This folder contains the config files that are used for training models using spaCy/Prodigy. These are useful for reproducability of training jobs.
These need to be stored locally should be saved in this location. This folder, and its sub-folders, are version-controlled.

## Creating a `config` file
Information on configs can be found here:
https://spacy.io/usage/training#quickstart

Users can use the tool on the link above to create a simple `base` config file.
This should be saved, ideally prefixing the file with `base_<<filename>>`

Users can then run
```
python -m spacy init fill-config path_to_config/base_<<config.cfg>> path_to_config/<<config.cfg>>
```
which will fill in the remaining defaults. Training configs should always be complete and without hidden defaults, to keep your experiments reproducible.

This config file can then be used when training models using spacy/prodigy ecosystem.

## Config files
1. config.cfg
    - standard base config file

2. trf_config.cfg
    - config file using transformer model
    - needs to be run on GPU, or takes a long time
    - requires transformer installs contained in the requirements.txt (`en_core_web_trf`, `spacy-transformers`)
