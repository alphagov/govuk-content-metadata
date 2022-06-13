## Notebook-like code to fix the training set after the sentences were accidentally segmented
# for step 2 when we annotated for the extra 8 categories: GPE, ORG PN, PERSON PN, POSTCODE, EMAIL, PHONE N, DATE, MONEY £ 

# This required a hack to ensure we could merge those annotations with the original annotation for FORM

# This code addresses this.

# REQUIREMENT: need to have prodigy installed: prodigy>=1.11.0,<2.0.0


from email import generator
from typing import List
import spacy
from prodigy.components.loaders import JSONL
from prodigy.components.preprocess import split_sentences
import collections
import json

# STEP 1 - read original 2975 sentences annotated for FORM
source = 'data/gold//forms_rh_at_3000.jsonl'
# unsegmented
stream = JSONL(source)

# STEP 2 - add unique ID
# we'll add a unique id to each example/sentence so that we can then stick them back together 
# after the accidental segmentation
def add_unique_id(stream: generator) -> generator:
    for i, el in enumerate(stream):
        el['enum_id'] = i
        yield el

stream_enum = add_unique_id(stream) 

stream_list = list(stream_enum)

# let's run some basic stats
len(stream_list)
# 2975 
len(set([d['_input_hash'] for d in stream_list]))
# 2970
len(set([d['text'] for d in stream_list]))
# 2970

# there seem to be 5 duplicates

# duplicates texts?
duplicates_stream = [item for item, count in collections.Counter([d['text'] \
    for d in stream_list]).items() if count > 1]
len(duplicates_stream)
# 5 yep



# STEP 3 - Segment the original sample (annotated for FORM)
# This is to obtain exactly the segmented sample as accidentally obtained before annotatiing for teh tehr 8 categories
# We had checked separately that, luckily, examples are segmented exactly in the same way.

nlp = spacy.load('en_core_web_lg')
# need to re-load the data as the generator has been "used"
stream = JSONL(source)
stream_enum = add_unique_id(stream) 
segmented_stream_ids = split_sentences(nlp, stream_enum)

segmented_stream_list = list(segmented_stream_ids)

# Let's run some basic stats here too
len(segmented_stream_list)
# 3731
len(set([d['_input_hash'] for d in segmented_stream_list]))
# 3478
len(set([d['text'] for d in segmented_stream_list]))
# 3478

# again more duplicates after segmenting...

# let's confirm - duplicates texts?
duplicates_segmented_stream = [item for item, count in collections.Counter([d['text'] \
    for d in segmented_stream_list]).items() if count > 1]
len(duplicates_segmented_stream)
#110

# STEP 4 - load two (segmented) samples annotated for 8 extra entity types by RH and AT
source_at = "data/gold/sample_goppepdm_at_correct_1488.jsonl"
stream_at = JSONL(source_at)

source_rh = "data/gold/sample_goppepdm_rh_correct_1487.jsonl"
stream_rh = JSONL(source_rh)

stream_at_list = list(stream_at)
stream_rh_list = list(stream_rh)

len(stream_at_list)
# 1939
len(stream_rh_list)
# 1626

# just extract the texts for some exploration
stream_at_texts = [d['text'] for d in stream_at_list]
stream_rh_texts = [d['text'] for d in stream_rh_list]
stream_at_rh_texts = stream_at_texts + stream_rh_texts 

len(stream_at_rh_texts)
#3565 
# NOTE: we probably haven't annotated every example
len(set(stream_at_rh_texts))
#3444

# duplicates...

duplicates_at = [item for item, count in collections.Counter(stream_at_texts).items() if count > 1]
len(duplicates_at)
# 48
duplicates_rh = [item for item, count in collections.Counter(stream_rh_texts).items() if count > 1]
len(duplicates_rh)
# 4
duplicates_rh_at = [item for item, count in collections.Counter(stream_at_rh_texts).items() if count > 1]
len(duplicates_rh_at)
# 88

# Let's have a look at the duplicates
stream_at_rh_list = stream_at_list + stream_rh_list
duplicates_rh_at = [d for d in stream_at_rh_list if d['text'] in duplicates_rh_at]
len(duplicates_rh_at)

dup_list = []
for d in duplicates_rh_at:
    dup_list.append({k:v for k,v in d.items() if k in ['text', 'spans', '_annotator_id']})
len(dup_list)
dup_list = sorted(dup_list, key=lambda d: d['text']) 

# we'll just keep one annotation example for each text, regardless of annotator or annotation
# on the assumption that the same text would have been annotated exactly the same way
# so annotator or annotation instance shouldn't matter
def remove_dupes(l: List[dict], k: str) -> List[dict]:
    """remove duplicates from a list of dictionary where duplicates are identified based on the values
    of one key `k`
    
    example: 
    dd = [{'a': 123, 'b': 111}, {'a': 123, 'b': 222}, {'a': 456, 'b': 111}]
    remove_dub(dd, 'a')
    [{'a': 123, 'b': 111}, {'a': 456, 'b': 111}]

    """
    seen = {} 
    dedup_out = []
    for d in l:
        v = d[k]
        if v not in seen:
            seen[v] = d
            dedup_out.append(d)
    return dedup_out

dedup = remove_dupes(dup_list, 'text')
len(dedup)  # 88 GOOD

# That was just a test
# let's apply it to the original segmented set now
len(stream_at_rh_list)
#3565
stream_at_rh_list_dedup = remove_dupes(stream_at_rh_list, 'text')
len(stream_at_rh_list_dedup)
# 3444 GOOD

# check
[item for item, count in collections.Counter([d['text'] \
    for d in stream_at_rh_list_dedup]).items() if count > 1]


# STEP 4 - match batch2 segmented samples to the original sample annotated for FORM (segmented version first!)

# we need to match them (via text) to the original annotated only for FORM
# here the segmented version
len(segmented_stream_list)
#3731

# let's deduplicate this as well by text
segmented_stream_list_dedup = remove_dupes(segmented_stream_list, 'text')
len(segmented_stream_list_dedup)
#3478

len(set([d['enum_id'] for d in segmented_stream_list_dedup]))
# 2966


matches = []
nonmatches = []
batch2_texts = [d['text'] for d in stream_at_rh_list_dedup]
for dd in segmented_stream_list_dedup:
    if dd['text'] in batch2_texts:
        for d in stream_at_rh_list_dedup:
            if d['text'] == dd['text']:
                for el in d['spans']:
                    dd['spans'].append(el)
        matches.append(dd)
    else: 
        nonmatches.append(dd)   


len(matches)
# 3444 NICE

# Check
# example with both batches of entities annotated
matches[2000]['text']
matches[2000]['spans']   # yep, both FORM and other category types
matches[2000]['enum_id']


# STEP 5 - combine with the original UNSEGMENTED sample via enum_id
len(stream_list)

# deduplicate by text as well
stream_list_dedup = remove_dupes(stream_list, 'text')
len(stream_list_dedup)
#2970 GOOD

len(matches)
# 3444

new_matches = []
new_nonmatches = []

for dd in stream_list_dedup:
    for d in matches:
        if d['enum_id'] == dd['enum_id']:
            for el in d['spans']:
                # avoiding adding FORM annotation which is already in there
                if el not in dd['spans']:
                    dd['spans'].append(el)
    new_matches.append(dd)

len(new_matches)
# 2970 GOOD

# check
[d['text'] for d in new_matches if (d['enum_id'] == 1577)]
[d['spans'] for d in new_matches if (d['enum_id'] == 1577)]

new_matches[2000]['text']
new_matches[2000]['spans']

# only thing: the input_hash has may not be the same for different elems of spans

# STEP 6 - export as JSONL
OUPUT_FILEPATH = 'data/training_set/sample_step2_form_goppepdm.jsonl'

with open(OUPUT_FILEPATH, 'w') as fp:
    for item in new_matches:
        fp.write(json.dumps(item, ensure_ascii=False) + "\n")
