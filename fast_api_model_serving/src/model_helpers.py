from spacy.language import Language


def combine_ner_components(ner_trf1: Language, ner_trf2: Language) -> Language:
    """
    Takes in two spacy transformer pipeline objects, each containing a Named Entity Recognition (NER)
    component, and returns a new spacy pipeline object that combines the two NER components.

    Args:

        ner_trf1: the first spacy transformer pipeline containing a NER component to be combined
        ner_trf2: the second spacy transformer pipeline containing a NER component to be combined

    Returns:
        a new spacy pipeline object that combines the two NER components,
        placing the ner_trf2 NER component before the ner_trf1 NER component.

    Ref: https://github.com/explosion/projects/tree/v3/tutorials/ner_double
    """
    # give this component a copy of its own tokenizer
    ner_trf2.replace_listeners("transformer", "ner", ["model.tok2vec"])
    # put the second ner component before the other ner
    ner_trf1.add_pipe("ner", name="ner_2", source=ner_trf2, before="ner")
    print(ner_trf1.pipe_names)
    return ner_trf1
