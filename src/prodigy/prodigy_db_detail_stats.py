import prodigy
from prodigy.components.db import connect
from collections import Counter
from prodigy.util import split_string
from typing import List, Optional

@prodigy.recipe(
    "db-detail-stats",
    datasets=("One or more comma-separated datasets", "option", "d", split_string),
    )

def db_detail_stats(
    datasets: Optional[List[str]] = None,
):
    """
    This custom recipe gets counts of entities in an annotated database. It outputs the name of each database put into the command, as well as the stats.
    """
    #connect to database in .prodigy config
    db = connect()
    for d in datasets:
        print(d)
        # check if dataset is in the database
        if d not in db:
            raise ValueError("Dataset not in DB.")
        #get database into list
        examples = db.get_dataset(d)
        #for each entry (annotated line) in database, get the annotated 'spans'
        #add to count of spans iteratively
        counts = Counter()
        for eg in examples:
            for span in eg.get("spans", []):
                counts[span["label"]] += 1
        #print summary of counted entities
        print(counts)

