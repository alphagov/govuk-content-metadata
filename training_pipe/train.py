import spacy
import thinc_gpu_ops
from spacy.cli.train import train

if __name__ == "__main__":

    thinc_gpu_ops.AVAILABLE

    spacy.require_gpu()

    # train("./config.cfg", overrides={"paths.train": "./train.spacy", "paths.dev": "./dev.spacy"})
    train(
        config_path="phase_1_trf_config.cfg",
        use_gpu=0,
        overrides={
            "paths.train": "phase_1_corpus/train.spacy",
            "paths.dev": "phase_1_corpus/train.spacy",
        },
    )
