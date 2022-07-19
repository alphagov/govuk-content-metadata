example_ins = {
    "base_path": "/example1",
    "title_ents": [("UK", "GPE", 1, 2), ("EU", "ORG", 5, 6)],
    "description_ents": [
        ("UK", "GPE", 6, 7),
        ("EU", "ORG", 9, 10),
        ("2016", "DATE", 11, 12),
    ],
    "text_ents": [
        ("UK", "GPE", 16, 17),
        ("EU", "ORG", 19, 20),
        ("2016", "DATE", 11, 12),
        ("UK", "GPE", 19, 20),
        ("Teresa May", "PERSON", 21, 23),
        ("President Tusk", "PERSON", 33, 35),
        ("£34 million", "MONEY", 76, 78),
    ],
}

example_outs_1 = {
    "base_path": "/example1",
    "entities": {
        {
            "entity_name": "UK",
            "entity_type": "GPE",
            "weight": 4,
            "in_title": True,
            "in_desc": True,
            "in_text": True,
        },
        {
            "entity_name": "EU",
            "entity_type": "ORG",
            "weight": 3,
            "in_title": True,
            "in_desc": True,
            "in_text": True,
        },
        {
            "entity_name": "2016",
            "entity_type": "DATE",
            "weight": 2,
            "in_title": False,
            "in_desc": True,
            "in_text": True,
        },
        {
            "entity_name": "Theresa May",
            "entity_type": "PERSON",
            "weight": 1,
            "in_title": False,
            "in_desc": False,
            "in_text": True,
        },
        {
            "entity_name": "President Tusk",
            "entity_type": "PERSON",
            "weight": 1,
            "in_title": False,
            "in_desc": False,
            "in_text": True,
        },
        {
            "entity_name": "£34 million",
            "entity_type": "MONEY",
            "weight": 1,
            "in_title": False,
            "in_desc": False,
            "in_text": True,
        },
    },
}

example_outs_2 = {
    "base_path": "/example1",
    "entities": [
        {"entity_name": "UK", "entity_type": "GPE", "weight": [1, 1, 2]},
        {"entity_name": "EU", "entity_type": "ORG", "weight": [1, 1, 1]},
        {"entity_name": "2016", "entity_type": "DATE", "weight": [0, 1, 1]},
        {"entity_name": "Theresa May", "entity_type": "PERSON", "weight": [0, 0, 1]},
        {"entity_name": "President Tusk", "entity_type": "PERSON", "weight": [0, 0, 1]},
        {"entity_name": "£34 million", "entity_type": "MONEY", "weight": [0, 0, 1]},
    ],
}


def dict_wrangle(json_in):
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
    setty = set(title_ents + description_ents + text_ents)  # get a set of unique tuples
    entities = []  # instantiate list
    for i in setty:
        title_count, desc_count, text_count = (
            title_ents.count(i),
            description_ents.count(i),
            text_ents.count(i),
        )  # count occurences of tuple in each location
        weight = [title_count, desc_count, text_count]  # create weight arra
        entry = {
            "entity_name": i[0],
            "entity_type": i[1],
            "weight": weight,
        }  # convert entry to dict
        entities.append(entry)  # append disct to list

    return {"base_path": base_path, "entities": entities}  # return dictionary
