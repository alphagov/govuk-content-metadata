# Stratified sampling of GOV.UK base_path's

## Restore the content store as a MongoDB database
You will need

- AWS permissions and tools to access the GOV.UK integration environment.
- A download recent copy of the GOV.UK content store as a .bson.
- To restore the content store as a MongoDB.

Follow this [guidance](https://github.com/ukgovdatascience/govuk-mongodb-content) to create a MongoDB instance of the GOV.UK content store with Docker.


## Produce stratified samples of GOV.UK content

This module produces two samples of the GOV.UK content:
- one stratified by level-1 taxons
- one stratified by schema_name + document_type


### Preprocess the content store

From the root directory of this project, run:

To preprocess the content store (needed only once)
```shell
python -m  src.strata.strata
```

### Produce the samples

To produce the samples:

- Specify the size for the two samples in `src/strata/sample_sizes.yaml`.
- Specify the weights for the strata in: `src/strata/schemas_weights.yaml` and `src/strata/taxons_weights.yaml`. Weight < 1 means you’ll under sample that strata. Weight > 1 means you’ll over sample that strata. 


Then, from the root directory of this project, run:

```shell
python -m src.strata.sample_paths_by_strata
```

The samples are saved as CSV in `src/strata/data`.
