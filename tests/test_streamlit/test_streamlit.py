import pandas as pd
import pytest
import requests
from unittest.mock import Mock
from bs4 import BeautifulSoup


from src.ner_streamlit_app.utils import (
    get_model_metrics,
    get_model_ents_metrics,
    _get_page_soup,
    _get_sents_from_soup
    )

def test_get_model_metrics_with_mock():
    # Create a mock spacy model with performance metrics
    mock_model = Mock()
    mock_model.meta = {
        "performance": {
            "ents_f": 0.9,
            "ents_p": 0.8,
            "ents_r": 1.0
        }
    }

    # Call the function and check the returned metrics
    metrics = get_model_metrics(mock_model)
    assert metrics["model_f"] == 0.9
    assert metrics["model_p"] == 0.8
    assert metrics["model_r"] == 1.0

def test_get_model_ents_metrics_with_mock():
    # Create a mock spacy model with entity metrics
    mock_model = Mock()
    mock_model.meta = {
        "performance": {
            "ents_per_type": {
                "ORG": {"p": 0.9, "r": 0.8, "f": 0.85},
                "PERSON": {"p": 0.95, "r": 0.85, "f": 0.9},
                "GPE": {"p": 0.8, "r": 0.95, "f": 0.87}
            }
        }
    }

    # Call the function and check the returned DataFrame
    df = get_model_ents_metrics(mock_model)
    expected_df = pd.DataFrame({
        "ORG": {"p": 0.9, "r": 0.8, "f": 0.85},
        "PERSON": {"p": 0.95, "r": 0.85, "f": 0.9},
        "GPE": {"p": 0.8, "r": 0.95, "f": 0.87}
    }).T
    pd.testing.assert_frame_equal(df, expected_df)


# define test fixtures
@pytest.fixture
def sample_url():
    return "https://www.example.com"

# test cases
def test_get_page_soup_returns_soup_object(sample_url):
    soup = _get_page_soup(sample_url)
    assert isinstance(soup, BeautifulSoup)

def test_get_page_soup_raises_exception_on_invalid_url():
    with pytest.raises(requests.exceptions.RequestException):
        _get_page_soup("invalid_url")

def test_get_page_soup_raises_exception_on_missing_url():
    with pytest.raises(TypeError):
        _get_page_soup()


# define test fixtures
@pytest.fixture
def sample_soup():
    html = "<html><body><div class='gem-c-govspeak'>This is a sentence.<br> This is another sentence.</div></body></html>"
    return BeautifulSoup(html, "html.parser")

# test cases
def test_get_sents_from_soup_returns_list(sample_soup):
    sents = _get_sents_from_soup(sample_soup)
    assert isinstance(sents, list)

def test_get_sents_from_soup_returns_cleaned_sentences(sample_soup):
    sents = _get_sents_from_soup(sample_soup)
    assert sents == [['This is a sentence. This is another sentence.']]

def test_get_sents_from_soup_returns_empty_list_on_empty_soup():
    sents = _get_sents_from_soup(None)
    assert sents == []

def test_get_sents_from_soup_returns_empty_list_on_missing_body_class(sample_soup):
    sample_soup.body.div['class'] = 'some_other_class'
    sents = _get_sents_from_soup(sample_soup)
    assert sents == []