# from spacy.cli.train import train
import json

with open("data/training_set/phase_1_annotations.jsonl", "rb") as f:
    result = [json.loads(jline) for jline in f.read().splitlines()]

# if __name__ == "__main__":

#     train("./config.cfg", overrides={"paths.train": "./train.spacy", "paths.dev": "./dev.spacy"})
