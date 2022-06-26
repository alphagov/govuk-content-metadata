import os
import pandas as pd

from src.make_strata.extract_content_store import ContentStore

pd.set_option("display.max_colwidth", None)

SAMPLES_DIR = "src/make_strata/data/"
SAMPLES_DATE = "20220622"
SAMPLE_DOCTYPES = f"{SAMPLES_DATE}_schemas_stratified_random_sample.csv"
SAMPLE_TAXONS = f"{SAMPLES_DATE}_taxons_stratified_random_sample.csv"

OUTPUTFILE = os.path.join(
    SAMPLES_DIR, f"{SAMPLES_DATE}_stratified_sample_all_content.csv"
)

sample_doctypes = pd.read_csv(os.path.join(SAMPLES_DIR, SAMPLE_DOCTYPES))
sample_taxons = pd.read_csv(os.path.join(SAMPLES_DIR, SAMPLE_TAXONS))

sample_all_pagepaths = set(
    list(sample_doctypes.base_path) + list(sample_taxons.base_path)
)
print(f"Number of unique page_paths: {len(sample_all_pagepaths)}")
pagepaths_list = list(sample_all_pagepaths)

content_store = ContentStore()
content_store_df = content_store.extract_content()
print(f"size of content store extract: {content_store_df.shape}")

content_store_df.to_csv(OUTPUTFILE, index=False)
