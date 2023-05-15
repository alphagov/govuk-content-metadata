## SQL queries

The sql queries are saved as .txt files to ease compatibilty with the `storage.googleapis.com/download/storage/v1/b/` api.

# get_new_content

This SQL script identifies and extracts the content of those GOV.UK pages that were either:
- significantly changed (major update)
- newly created
the day before ('yesterday').

Pages are further filtered to only include those whose:
- locale is English,
- status in beta or live
- document type indicates they do contain actual content.

# postprocess_predictions

This SQL script extract the raw entities from the bigquery table that was the output of the Vertex AI batch prediction job and save them to a suitable format for downstream use.

It also attach to each (lower case) entity instance and assigned type a unique URI, constructed as:

`'https://www.gov.uk/named-entity/' + type + '/' + ENCODE_URI_COMPONENT(LOWER(name))`.

For instance, for the entity name "England" classified as "GPE", the URI will be:
"https://www.gov.uk/named-entity/GPE/england".

# count_entities

SQL script to aggregate and count entities per GOV.UK url.

# update_entity_accumulation

SQL script to:
- append the entities extracted from content that were newly created the previous day
- replace the entities extracted from content that changed the previous day.

This is done in three steps:
1. Extract the unique urls that were changed or were newly created the day before;
2. Delete the entries corresponding to these urls from the tables that have been collecting the extracting entities;
3. Add the entries with the extracted entities for all the affected urls (as for step 1.) to the tables that have been accumulating extracting entities
