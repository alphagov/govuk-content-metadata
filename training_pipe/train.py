import spacy
from spacy.cli.train import train

if __name__ == "__main__":

    import time

    if spacy.require_gpu():
        print("GPU good to go :D")

    start = time.time()
    train(
        config_path="phase_1_trf_config.cfg",
        use_gpu=0,
        overrides={
            "paths.train": "phase_1_corpus/train.spacy",
            "paths.dev": "phase_1_corpus/dev.spacy",
        },
    )
    print(time.time() - start)
    print("Training completed.")
