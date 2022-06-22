import pandas as pd
import yaml
from typing import Dict


def get_stratified_sample(
    df: pd.DataFrame, strata_col: str, weights: Dict[str, int], sample_size: int
) -> pd.DataFrame:
    """ """
    df = df.copy()
    num_strata = len(weights)
    size_strata_if_equal_size = int(round(sample_size / num_strata, 0))
    weighted_size_strata = {
        stratum: int(round(weight * size_strata_if_equal_size, 0))
        for stratum, weight in weights.items()
    }

    df = df.groupby(strata_col, as_index=False).apply(
        lambda x: x.sample(n=weighted_size_strata[x.name])
    )

    return df


if __name__ == "__main__":

    import os
    from datetime import date

    import argparse

    strata_parser = argparse.ArgumentParser(
        description="Run src.strata.sample_paths_by_strata"
    )

    # Define the positional arguments we want to get from the user
    strata_parser.add_argument(
        "-sample_size_taxons",
        type=int,
        action="store",
        dest="taxons_size",
        required=True,
        help="specify number of pages to sample from strata by taxons",
    )

    strata_parser.add_argument(
        "-sample_size_doctype",
        type=int,
        action="store",
        dest="doctype_size",
        required=True,
        help="specify number of pages to sample from strata by doc types",
    )

    strata_args = strata_parser.parse_args()
    SCHEMA_DOCS_SAMPLE_SIZE = strata_args.doctype_size
    TAXONS_SAMPLE_SIZE = strata_args.taxons_size

    today = date.today().strftime("%Y%m%d")
    STRATA_TAXON_OUTPUT = f"{today}_taxons_stratified_random_sample.csv"
    STRATA_DOCTYPE_OUTPUT = f"{today}_schemas_stratified_random_sample.csv"
    STRATA_TAXON_OUTPATH = os.path.join("src/strata/data", STRATA_TAXON_OUTPUT)
    STRATA_DOCTYPE_OUTPATH = os.path.join("src/strata/data", STRATA_DOCTYPE_OUTPUT)

    STRATA_INPUT_FILEPATH = "src/strata/data/strata_schema_docs_taxons.csv"
    strata_df = pd.read_csv(STRATA_INPUT_FILEPATH)

    SCHEMA_STRATA_DEFINITIONS = "src/strata/schema_strata_definition.csv"
    schema_strata_defs = pd.read_csv(SCHEMA_STRATA_DEFINITIONS)

    with open("src/strata/schemas_weights.yaml", "r") as file:
        SCHEMAS_WEIGHTS = yaml.safe_load(file)
    with open("src/strata/taxons_weights.yaml", "r") as file:
        TAXONS_WEIGHTS = yaml.safe_load(file)

    # add "schema_strata_name" (i.e., the schema/docs strata) as column to strata_df
    strata_df = strata_df.merge(
        schema_strata_defs, on=["schema_name", "document_type"], how="left"
    )

    # rename null value as "Unspecified" taxons
    strata_df.rename(columns={"taxon_level1": "taxon_level1_orig"}, inplace=True)
    strata_df["taxon_level1"] = [
        "Unspecified" if (row is None or isinstance(row, float)) else row
        for row in strata_df.taxon_level1_orig
    ]

    # stratified random sample by schemas/document_types
    schemas_stratified_random_sample_df = get_stratified_sample(
        strata_df, "schema_strata_name", SCHEMAS_WEIGHTS, SCHEMA_DOCS_SAMPLE_SIZE
    )
    print(
        "Stratified random sample by Schema name/Document type: sample sizes by strata"
    )
    print(
        schemas_stratified_random_sample_df.groupby(
            "schema_strata_name"
        ).base_path.count()
    )
    schemas_stratified_random_sample_df[
        ["schema_name", "document_type", "schema_strata_name", "base_path"]
    ].to_csv(STRATA_DOCTYPE_OUTPATH, index=False)

    # stratified random sample by taxons
    taxons_stratified_random_sample_df = get_stratified_sample(
        strata_df, "taxon_level1", TAXONS_WEIGHTS, TAXONS_SAMPLE_SIZE
    )
    print("Stratified random sample by Taxons: sample sizes by strata")
    print(taxons_stratified_random_sample_df.groupby("taxon_level1").base_path.count())
    taxons_stratified_random_sample_df[["taxon_level1", "base_path"]].to_csv(
        STRATA_TAXON_OUTPATH, index=False
    )
