import tqdm
import json
import spacy
import pandas as pd

# disabled unnecessary spacy NLP pipeline components
disabled_pipelines = [
    "tok2vec",
    "tagger",
    "parser",
    "lemmatizer",
    "attribute_ruler",
]
added_pipeline = "sentencizer"
nlp = spacy.load("en_core_web_lg", disable=disabled_pipelines)
nlp.add_pipe(added_pipeline)


def load_preprocessed_content_store(path_to_gz):
    """
    Load the preprocessed content store (ppcs) into a DataFrame.
    You can get the ppcs from 'govuk-data-integration' S3 bucket.
    """
    print("Loading preprocessed content store .gz")
    df = pd.read_csv(path_to_gz, compression="gzip", header=0, sep="\t")
    print("Loaded successfully. Shape: {}".format(df.shape))
    return df


def get_base_path_sample_list(base_path_file, col):
    base_paths_df = pd.read_csv(base_path_file)
    base_paths_list = list(base_paths_df[col])
    return base_paths_list


def filter_content_store_by_basepathlist(dataframe, base_path_col, base_path_list):
    """
    Filter preprocessed content store by base path list.
    """
    print("Shape before filter: {}".format(df.shape))
    df_filt = dataframe[dataframe[base_path_col].isin(base_path_list)]
    print("Shape after filter: {}".format(df_filt.shape))
    return df_filt


def trim_dataframe(dataframe, columns=[]):
    """
    Trim a DataFrame to only include columns of interest.
    """
    cols_before = [i for i in dataframe.columns]
    df = dataframe[[col for col in columns]]
    cols_after = [i for i in df.columns]
    print("Columns before trim: {}".format(cols_before))
    print("Columns after trim: {}".format(cols_after))
    return df


def text_to_sents(text):
    """
    Split a blob of text into sentences using SpaCy function.
    """

    if isinstance(text, float):
        return []

    doc = nlp(text)
    assert doc.has_annotation("SENT_START")
    sent_list = [sent.text.strip() for sent in doc.sents]
    return sent_list


def text_col_to_sents2(dataframe, text_col, new_col):
    """
    Turn a text column of a DataFrame into a column of sentences.
    """
    dataframe[new_col] = dataframe[text_col].apply(lambda x: text_to_sents(x))
    return dataframe


def text_col_to_sents(df, text_col):
    """
    Turn a text column of a DataFrame into a column of sentences.
    """
    return df[text_col].apply(lambda x: text_to_sents(x))


def sentences_to_jsonl(dataframe, sentence_col, meta_cols, outfile):
    """
    Convert a column containing list of sentences for each row into .jsonl file format for Prodigy.
    Specify metacols and file path to save .jsonl to.
    """
    dict_lines = []
    for i, row in tqdm(dataframe.iterrows()):
        for sentence in row[sentence_col]:
            # dict_line = {"text": sentence, "meta": {"base_path": base_path, "content_id": c_id}}
            dict_line = {"text": sentence, "meta": {i: row[i] for i in meta_cols}}
            dict_lines.append(dict_line)
    with open(outfile, "w") as jsonlfile:
        jsonlfile.write("\n".join(json.dumps(j) for j in dict_lines))


if __name__ == "__main__":

    import os
    import time
    import dask.dataframe as dd

    DIR_STRATA = os.getenv("DIR_SRC_STRATA")
    DIR_OUTPUT = os.getenv("DIR_DATA_PROCESSED")

    ramdom_schemas_filepath = os.path.join(
        DIR_STRATA, "data", "schemas_stratified_random_sample.csv"
    )
    ramdom_taxons_filepath = os.path.join(
        DIR_STRATA, "data", "taxons_stratified_random_sample.csv"
    )
    output_filepath = os.path.join(DIR_OUTPUT, "sampled_sentences.jsonl")

    df = load_preprocessed_content_store(
        path_to_gz="/tmp/govukmirror/preprocessed_content_store_250522.csv.gz"
    )
    base_path_schema_list = get_base_path_sample_list(
        ramdom_schemas_filepath, col="base_path"
    )
    base_path_taxon_list = get_base_path_sample_list(
        ramdom_taxons_filepath, col="base_path"
    )
    base_path_list = set(base_path_schema_list + base_path_taxon_list)
    df_filt = filter_content_store_by_basepathlist(
        df, base_path_col="base_path", base_path_list=base_path_list
    )
    df_trim = trim_dataframe(df_filt, columns=["base_path", "content_id", "text"])

    print("Preprocessing sentences...")
    tic = time.perf_counter()
    ddf = dd.from_pandas(df_trim, npartitions=os.cpu_count())
    res = ddf.map_partitions(lambda df: text_col_to_sents(df, "text"))
    out = res.compute()
    df_trim = df_trim.assign(sentences=out)
    toc = time.perf_counter()
    print(f"Preprocessing of sentences - Completed in in {toc - tic:0.4f} seconds")

    sentences_to_jsonl(
        df_trim,
        sentence_col="sentences",
        meta_cols=["base_path", "content_id"],
        outfile=output_filepath,
    )
