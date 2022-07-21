import pytest
from src.utils.mdl_to_govgraph import jsonl_to_govgraph, list_wrangle


in_data = "data/processed/entities_title_10000.jsonl"
out_data = "data/processed/entities_title_10000_out.jsonl"

in_list = [
    {"/": [["GOV.UK", "ORG", 0, 6], ["GOV.UK", "ORG", 9, 10], ["EU", "GPE", 20, 21]]},
    {
        "/aaib-reports/aerospatiale-as332l-super-puma-g-tigo-22-february-1992": [
            ["22 February 1992", "DATE", 40, 56]
        ]
    },
    {
        "/aaib-reports/aerospatiale-as350b-ecureuil-g-marc-and-bell-206b-g-bnit-13-november-1990": [
            ["13 November 1990", "DATE", 60, 76]
        ]
    },
    {
        "/aaib-reports/aerospatiale-as350b-squirrel-g-maho-14-march-1983": [
            ["14 March 1983", "DATE", 38, 51]
        ]
    },
    {
        "/aaib-reports/aerospatiale-as350b1-g-roin-27-june-1998": [
            ["27 June 1998", "DATE", 30, 42]
        ]
    },
]


# @pytest.mark.parametrize("test_input, test_expected")
def test_in_out_len_files():
    """Assert the in and out files are the same len."""
    in_data = "data/processed/entities_title_10000.jsonl"
    out_data = "data/processed/entities_title_10000_out.jsonl"
    jsonl_to_govgraph(in_data, out_data)
    assert sum(1 for line in open(in_data)) == sum(1 for line in open(out_data))


# @pytest.mark.parametrize("test_input, test_expected")
def test_in_out_len_lists():
    """Assert the in and out lists are the same len."""
    out = list_wrangle(in_list)
    assert len(in_list) == len(out)


@pytest.mark.parametrize(
    "input_file, output_file",
    [("turnip.jsonl", "turnip_out.jsonl"), ("desk.jsonl", "desk_out.jsonl")],
)
def test_value_error_is_raised(input_file, output_file):
    with pytest.raises(ValueError):
        jsonl_to_govgraph(input_file, output_file)
