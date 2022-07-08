# This script is designed to add a field to the metadata of annotations for .jsonl file
# The purpose initially arose because earlier annotations did not have a 'base_path' field in the metadata,
# meaning that scripts such as `get_confusion_matrix.py` could not run.

import json
import jsonlines

# with open('./data/gold/mark_goppepdm_3_after_review.jsonl', 'r') as json_file:
#     json_list = list(json_file)

examples = []

with jsonlines.open("./data/gold/mark_goppepdm_3_after_review.jsonl") as f:
    for line in f.iter():
        # print(line)
        examples.append(line)

# if 'base_path' not in 'meta', add 'Unknown' base path
for e in examples:
    if "meta" in e:
        if "base_path" in e["meta"]:
            continue
        elif "base_path" not in e["meta"]:
            e["meta"]["base_path"] = "Unknown"

with open("./data/gold/mark_goppepdm_3_after_review_withbase.jsonl", "w") as outfile:
    for entry in examples:
        json.dump(entry, outfile)
        outfile.write("\n")
