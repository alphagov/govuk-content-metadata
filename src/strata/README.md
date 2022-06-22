# Stratified sampling of GOV.UK base_path's

## 1. Restore the content store as a MongoDB database
You will need

- AWS permissions and tools to access the GOV.UK integration environment.
- A download recent copy of the GOV.UK content store as a .bson.
- To restore the content store as a MongoDB.

Follow this [guidance](https://github.com/ukgovdatascience/govuk-mongodb-content) to create a MongoDB instance of the GOV.UK content store with Docker.


## 2. Produce stratified samples of GOV.UK content

This module produces two samples of the GOV.UK content:
- one stratified by level-1 taxons
- one stratified by schema_name + document_type


### 3. Preprocess the content store

From the root directory of this project, run:

To preprocess the content store (needed only once)
```shell
python -m  src.strata.strata
```

### 4. Produce the samples

To produce the samples:

- Specify the weights for the strata in: `src/strata/schemas_weights.yaml` and `src/strata/taxons_weights.yaml`. Weight < 1 means you’ll under sample that strata. Weight > 1 means you’ll over sample that strata.


Then, from the root directory of this project, run:

```shell
python -m src.strata.sample_paths_by_strata -sample_size_taxons XXX -sample_size_doctype YYY
```

where `XXX` is the aimed-at sample size for the sample of page_path's stratified by taxons, and `YYY` is the aimed at sample size for the sample stratified by schema name/ document types.

The samples are saved as CSV in `src/strata/data` as `YYYYMMDD_schemas_stratified_random_sample.csv` and `YYYYMMDD_schemas_stratified_random_sample.csv` where `YYYYMMDD` is today's date.

Together with the samples of base_path's, two metadata files are also saved in `src/strata/data/`, containing the used weights and the actual sample sizes obtained for each strata: `YYYYMMDD_META_schemas_weights.csv` and `YYYYMMDD_META_taxons_weights.csv`.


### 5. Get Sentences from sample of base paths

The previous steps will output a list of base_paths that are sampled according to the strata.
The next step is to get sentences from the content on each of these base_paths.

1. Download a copy of the preprocessed_content store to a location on your machine. We will use: `/tmp/govukmirror/`

```
gds aws govuk-integration-datascience --assume-role-ttl 480m aws s3 cp s3://govuk-data-infrastructure-integration/knowledge-graph/2022-05-25/preprocessed_content_store_DDMMYY.csv.gz /tmp/govukmirror/
```

2. Make sure you have run the `src.strata.sample_paths_by_strata` module, Step 4 above. This will have created two lists of stratified-sampled base_paths, saved as csv files in `src/strata/data` and that will be use in the next step.

3. Ensure the relative data paths are aligned in `src.make_data.make_data` and run:

```shell
python -m src.make_data.make_data
```

The sentences .jsonl file is saved at `./data/processed/sampled_sentences.jsonl`.

You can then sample the sentences further if required.
