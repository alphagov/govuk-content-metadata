#this script merges two sets of annotations on the same dataset.

from prodigy.components.db import connect
from prodigy.models.ner import merge_spans

output_dataset_name = 'merged_dataset_script'

db = connect()  # connect to the DB using the prodigy.json settings
datasets_to_merge = ['sample_form_at_first80', 'sample_form_rh_correct', 'forms_rh_at_3000']
examples = []
for dataset in datasets_to_merge:
    examples += db.get_dataset(dataset)  # get examples from the database

db.add_dataset(output_dataset_name)

db.add_examples(examples, datasets=[output_dataset_name])


