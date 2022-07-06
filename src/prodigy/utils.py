from email.generator import Generator

from prodigy.components.loaders import JSONL


def load_stream(file_path: str) -> Generator:
    return JSONL(file_path)
