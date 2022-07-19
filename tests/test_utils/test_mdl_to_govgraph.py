from src.utils.mdl_to_govgraph import mdl_to_govgraph


example_ins = {
    "base_path": "/example1",
    "title_ents": [("UK", "GPE", 1, 2), ("EU", "ORG", 5, 6)],
    "description_ents": [
        ("UK", "GPE", 6, 7),
        ("EU", "ORG", 9, 10),
        ("2016", "DATE", 11, 12),
    ],
    "text_ents": [
        ("UK", "GPE", 16, 17),
        ("EU", "ORG", 19, 20),
        ("2016", "DATE", 11, 12),
        ("UK", "GPE", 19, 20),
        ("Teresa May", "PERSON", 21, 23),
        ("President Tusk", "PERSON", 33, 35),
        ("£34 million", "MONEY", 76, 78),
    ],
}

example_outs_2 = {
    "base_path": "/example1",
    "entities": [
        {"entity_name": "UK", "entity_type": "GPE", "weight": [1, 1, 2]},
        {"entity_name": "EU", "entity_type": "ORG", "weight": [1, 1, 1]},
        {"entity_name": "2016", "entity_type": "DATE", "weight": [0, 1, 1]},
        {"entity_name": "Theresa May", "entity_type": "PERSON", "weight": [0, 0, 1]},
        {"entity_name": "President Tusk", "entity_type": "PERSON", "weight": [0, 0, 1]},
        {"entity_name": "£34 million", "entity_type": "MONEY", "weight": [0, 0, 1]},
    ],
}


# @pytest.mark.parametrize("test_input, test_expected")
def test_same_base_path():
    """Assert the ``input_dict`` returns correctly."""
    out = mdl_to_govgraph(example_ins)
    assert out["base_path"] == example_outs_2["base_path"]


# @pytest.mark.parametrize("test_input, test_expected")
def test_same_keys():
    """Assert the ``input_dict`` returns correctly."""
    out = mdl_to_govgraph(example_ins)
    assert out.keys() == example_outs_2.keys()