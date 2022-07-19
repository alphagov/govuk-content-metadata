"""
This script contains a function that is used for wrangling outputs into format for Neo4j ingestion.
"""

from collections import OrderedDict


def mdl_to_govgraph(json_in):
    """Wrangle a dictionary into format for ingestion into Neo4j format.

    :param json_in: Input dictionary
    :type json_in: dict
    :return: Wrangled dictionary
    :rtype: dict
    """
    base_path = json_in["base_path"]  # base path is base path
    title_ents = [
        (a, b) for (a, b, _, _) in json_in["title_ents"]
    ]  # entity name and type from tuples only
    description_ents = [(a, b) for (a, b, _, _) in json_in["description_ents"]]
    text_ents = [(a, b) for (a, b, _, _) in json_in["text_ents"]]
    uniques = list(
        OrderedDict.fromkeys(title_ents + description_ents + text_ents)
    )  # get a set of unique tuples
    entities = []  # instantiate list
    for i in uniques:
        title_count, desc_count, text_count = (
            title_ents.count(i),
            description_ents.count(i),
            text_ents.count(i),
        )  # count occurences of tuple in each location
        weight = [title_count, desc_count, text_count]  # create weight array
        entry = {
            "entity_name": i[0],
            "entity_type": i[1],
            "weight": weight,
        }  # convert entry to dict
        entities.append(entry)  # append disct to list
    return {"base_path": base_path, "entities": entities}  # return dictionary
