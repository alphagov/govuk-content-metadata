import pandas as pd


def get_strata(content_store_df: pd.DataFrame) -> pd.DataFrame:
    """
    Args:
        content_store_df: a copy of the content store as pd.DataFrame. Output of ContentStore.extract() class method.
    Returns:
        A dataframe with base_path, schema_name, document_type and first-level taxon as columns.
        When a base_path has multiple first-level taxons, only one is kept.
    """
    taxons = filter_level1_taxon(content_store_df, "base_path", "taxons")
    taxons["taxon_level1"] = dictcolumn_to_col(taxons, "taxons", "title")
    taxons = taxons[["base_path", "taxon_level1"]].copy()

    # for base_path's with several of the same level-1 taxon
    taxons.drop_duplicates(inplace=True)
    # for base_path with more than one level-1 taxon, let's retain only one
    taxons.drop_duplicates(subset="base_path", keep="first", inplace=True)

    strata_df = pd.merge(
        content_store_df[
            ["base_path", "schema_name", "document_type", "publishing_app"]
        ],
        taxons,
        how="left",
        on="base_path",
        validate="one_to_one",
    )

    return strata_df


def filter_level1_taxon(df: pd.DataFrame, id_col: str, taxon_col: str) -> pd.DataFrame:
    """
    Only keep the level-1 taxon for each content item.
    Original index is preserved.
    """
    REPLACE_VALUE = {"title": "", "level": 1}

    taxons_df = df[[id_col, taxon_col]].copy()

    try:
        # each row contains exactly one dict: {id: val}
        exploded_df = taxons_df.explode(taxon_col).explode(taxon_col)

        # replace NaN with empty dict
        exploded_df = exploded_df.applymap(
            lambda x: REPLACE_VALUE if isinstance(x, float) else x
        )

        # return level-1 taxon only
        return exploded_df[
            [isinstance(x, dict) and x["level"] == 1 for x in exploded_df[taxon_col]]
        ]
    except Exception as e:
        print(e)


def dictcolumn_to_col(df: pd.DataFrame, dict_col: str, dict_value: str):
    """
    Return the dict[dict_value] as a separate column.
    """

    return df[dict_col].apply(lambda x: x.get(dict_value))


if __name__ == "__main__":

    from src.strata.extract_content_store import ContentStore

    content_store = ContentStore()
    content_store_df = content_store.extract()
    print(f"size of content store: {content_store_df.shape}")
    print(
        f"number of unique base_path in content_store_df: {content_store_df.base_path.nunique()}"
    )

    strata_df = get_strata(content_store_df)
    print(f"number of unique base_path in strata_df: {strata_df.base_path.nunique()}")

    STRATA_COUNTS_OUTPUT_FILEPATH = (
        "src/strata/data/strata_counts_schema_docs_pubapp_taxons.csv"
    )
    strata_df.groupby(
        ["publishing_app", "schema_name", "document_type", "taxon_level1"]
    )["base_path"].count().to_csv(STRATA_COUNTS_OUTPUT_FILEPATH, index=False)

    STRATA_OUTPUT_FILEPATH = "src/strata/data/strata_schema_docs_taxons.csv"
    strata_df.to_csv(STRATA_OUTPUT_FILEPATH, index=False)
