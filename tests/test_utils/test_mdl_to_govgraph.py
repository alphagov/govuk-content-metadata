import pytest
from src.utils.mdl_to_govgraph import (
    count_entity_occurrence,
    contains_alphanum,
    is_latin,
    only_roman_chars,
    begins_with_alphanumeric,
    clean_erroneous_names,
)


# tests contains_alphanum()
@pytest.mark.parametrize(
    "string, bool",
    [
        ("hello world", True),
        ("المملكة", True),
        ("Привет 123", True),
        ("***", False),
        ("hello []9", True),
        ("[]';]", False),
    ],
)
def test_contains_alphanum(string, bool):
    assert contains_alphanum(string) == bool


# tests is_latin()
@pytest.mark.parametrize(
    "char, bool",
    [
        ("h", True),
        ("w", True),
        ("ت", False),
        ("и", False),
        ("*", False),
        ("9", False),
        ("á", True),
    ],
)
def test_is_latin(char, bool):
    assert is_latin(char) == bool


# tests begins_with_alphanumeric()
@pytest.mark.parametrize(
    "string, bool",
    [
        ("hello", True),
        ("world", True),
        ("- org", False),
        ("*per", False),
        ("/foo", False),
        ("9bar", True),
    ],
)
def test_begins_with_alphanumeric(string, bool):
    assert begins_with_alphanumeric(string) == bool


# tests only_roman_chars()
@pytest.mark.parametrize(
    "string, bool",
    [
        ("hello", True),
        ("world", True),
        ("naïve", True),
        ("hello Россия", False),
        ("Hello, Zhōngguó", True),
        ("Hello, 中国人", False),
        ("المملكة العربية السعودية", False),
    ],
)
def test_only_roman_chars(string, bool):
    assert only_roman_chars(string) == bool


ex_input_1 = {
    "/cma-cases/continental-veyance": [
        ["CMA", "ORG", 4, 7],
        ["cma", "ORG", 12, 15],
        ["Continental AG", "ORG", 52, 66],
        ["Veyance Technologies Inc.", "ORG", 70, 95],
    ]
}
# should return
ex_output_1 = [
    ["/cma-cases/continental-veyance", "cma", "ORG", 2],
    ["/cma-cases/continental-veyance", "continental ag", "ORG", 1],
    ["/cma-cases/continental-veyance", "veyance technologies inc.", "ORG", 1],
]


def test_count_entity_occurrence():
    assert count_entity_occurrence(ex_input_1) == ex_output_1


ex_input_2 = {
    "/cma-cases/continental-veyance": [
        ["CMA", "ORG", 4, 7],
        ["cma", "ORG", 12, 15],
        ["Continental AG", "ORG", 52, 66],
        ["Veyance Technologies Inc.", "ORG", 70, 95],
        ["المملكة العربية السعودية", "ORG", 100, 101],
        ["-hello world", "PER", 105, 110],
    ]
}

# should return
ex_output_2 = {
    "/cma-cases/continental-veyance": [
        ["CMA", "ORG", 4, 7],
        ["cma", "ORG", 12, 15],
        ["Continental AG", "ORG", 52, 66],
        ["Veyance Technologies Inc.", "ORG", 70, 95],
    ]
}


def test_clean_erroneous_names():
    assert clean_erroneous_names(ex_input_2) == ex_output_2
