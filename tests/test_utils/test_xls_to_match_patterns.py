import pytest
import json
import pandas as pd
from pandas.util.testing import assert_frame_equal

from src.utils.xls_to_match_patterns import excel_to_df, df_to_match_patterns


@pytest.fixture
def excel_file(tmpdir):
    data = {
        "Sheet1": pd.DataFrame(
            {
                "EntityType": [10, 20, 30, 20, 15, 30, 45],
                "SeedTerm": [1, 2, 3, 4, 5, 6, 7],
            }
        ),
        "Sheet2": pd.DataFrame(
            {"EntityType": [50, 55, 60, 65], "SeedTerm": [8, 9, 10, 11]}
        ),
    }
    file_path = tmpdir.join("test.xlsx")
    with pd.ExcelWriter(file_path) as writer:
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return file_path


def test_excel_to_df(excel_file):
    expected_df = pd.DataFrame(
        {
            "EntityType": [10, 20, 30, 20, 15, 30, 45, 50, 55, 60, 65],
            "SeedTerm": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
        }
    )
    result_df = excel_to_df(excel_file, ["Sheet1", "Sheet2"])
    result_df.reset_index(drop=True, inplace=True)
    assert_frame_equal(expected_df, result_df)


@pytest.fixture
def test_data():
    data = {
        "EntityType": ["Fruit", "Animal", "Color"],
        "SeedTerm": ["green apple", "aloof and angry cat", "red"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def expected_output(tmpdir):
    expected_output_file = tmpdir.join("expected_output.jsonl")
    with open(expected_output_file, "w") as f:
        f.write(
            '{"label": "Fruit", "pattern": [{"LOWER": "green"}, {"LOWER": "apple"}]}\n'
        )
        f.write(
            '{"label": "Animal", "pattern": [{"LOWER": "aloof"}, {"LOWER": "and"}, {"LOWER": "angry"}, {"LOWER": "cat"}]}\n'
        )
        f.write('{"label": "Color", "pattern": [{"LOWER": "red"}]}\n')
    return expected_output_file


def test_df_to_match_patterns(test_data, tmpdir, expected_output):
    outfile = tmpdir.join("output.jsonl")
    df_to_match_patterns(test_data, outfile)

    with open(outfile, "r") as file:
        output = file.readlines()

    with open(expected_output, "r") as file:
        expected = file.readlines()

    assert len(output) == len(expected)
    for i in range(len(output)):
        assert json.loads(output[i]) == json.loads(expected[i])
