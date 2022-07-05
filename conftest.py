import spacy
import pytest


@pytest.fixture(scope="session")
def en_core_web_lg():
    return spacy.load("en_core_web_lg")
