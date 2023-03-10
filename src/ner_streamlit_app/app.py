import spacy
from spacy import displacy
import pandas as pd
import altair as alt
from spacy.tokens import Span
import streamlit as st
import numpy as np
from collections import Counter
from config import default_text
from config import colors as ent_colors
from utils import get_model_metrics, get_model_ents_metrics, url_get_sents

# page configuration
st.set_page_config(page_title="GovNER 2.0", page_icon="🧐", layout="wide")

# page main titles and description
st.title("Welcome to GovNER 2.0 🧐")
st.write("### Demonstration of NER on GOV.UK page")
st.write(
    "Data Products have developed a model that can detect entities of interest from 'govspeak' in GOV.UK content.",
    "Use the tool below on any GOV.UK url to see how it works.",
)

# sidebar component
with st.sidebar:
    ModelType = st.selectbox(
        "Choose your model",
        ["Transformer"],
        help="At present, you can choose our latest Transformer NER model to embed your text. More to come!",
    )

    # Select model - only one model for now
    if ModelType == "Transformer":
        # load transformermodel and cache
        @st.cache(allow_output_mutation=True)
        def load_model(model_path):
            """Load Transformer model.

            :param model_path: Path to Transformer model.
            :type model_path: str
            :return: Transformer pipeline.
            :rtype: Model.
            """
            nlp = spacy.load(model_path)
            return nlp

        # load bith models
        nlp_1 = load_model(model_path="./models/phase1_ner_trf_model/model-best")
        nlp_2 = load_model(model_path="./models/phase2_ner_trf_model/model-best")

    # displacy metric for loaded models
    metrics_1 = get_model_metrics(nlp_1)
    metrics_2 = get_model_metrics(nlp_2)
    # average headline metrics of the two models
    st.metric(
        label="Average F-Score",
        value=np.round(np.mean([metrics_1["model_f"], metrics_2["model_f"]]), 3),
        delta="1st",
    )
    st.metric(
        label="Average Precision",
        value=np.round(np.mean([metrics_1["model_p"], metrics_2["model_p"]]), 3),
        delta="1st",
    )
    st.metric(
        label="Average Recall",
        value=np.round(np.mean([metrics_1["model_r"], metrics_2["model_r"]]), 3),
        delta="1st",
    )
    # display detailed entity metrics in sidebar table
    ents_metrics_1 = get_model_ents_metrics(nlp_1)
    ents_metrics_2 = get_model_ents_metrics(nlp_2)
    ents_metrics = pd.concat([ents_metrics_1, ents_metrics_2])
    st.table(ents_metrics)

# text input and processing
with st.expander("Input text"):
    input_type = st.radio(
        "Would you like to run NER on free text or a GOV.UK page?",
        ("Free Text", "Custom GOV.UK URL", "Random GOV.UK URL"),
    )

    if input_type == "Free Text":
        text_area = st.text_area(
            "Insert text for NER here", value=default_text, height=150, max_chars=600
        )

        doc_1 = nlp_1(text_area)
        doc_2 = nlp_2(text_area)

    if input_type == "Custom GOV.UK URL":
        text_input = st.text_input(
            "Insert GOV.UK URL",
            value="https://www.gov.uk/government/people/elizabeth-truss",
        )
        text = url_get_sents(text_input)
        text = " ".join(text)

        doc_1 = nlp_1(text)
        doc_2 = nlp_2(text)

    if input_type == "Random GOV.UK URL":

        text = url_get_sents("https://www.gov.uk/random")
        text = " ".join(text)

        doc_1 = nlp_1(text)
        doc_2 = nlp_2(text)

        if st.button("Generate Random GOV.UK URL"):
            text = url_get_sents("https://www.gov.uk/random")
            text = " ".join(text)

            doc_1 = nlp_1(text)
            doc_2 = nlp_2(text)

# visualisations
col1, col2 = st.columns([2, 1])
with col1:

    # taken from https://spacy.io/usage/visualizers
    # set entities as spans for both model outputs - note - doc must be the same to merge
    doc_1.spans["sc"] = [
        Span(doc_1, ent.start, ent.end, ent.label_) for ent in doc_1.ents
    ]
    doc_1.spans["sc"] += [
        Span(doc_1, ent.start, ent.end, ent.label_) for ent in doc_2.ents
    ]

    # Create span visualisation using displacy
    options = {"colors": ent_colors}
    ent_html = displacy.render(doc_1, style="span", jupyter=False, options=options)
    # Display the entity visualization in the browser:
    st.markdown(ent_html, unsafe_allow_html=True)

with col2:
    # entity and label counts visualisation

    # get the list of entities from both models
    ents = [i for i in doc_1.ents] + [i for i in doc_2.ents]
    # get the list of labels from both models
    labels = [e.label_ for e in doc_1.ents] + [e.label_ for e in doc_2.ents]
    # count occurences
    entity_counts = Counter(labels)
    data = pd.DataFrame(
        {
            "Entity": [i for i in entity_counts.keys()],
            "Count": [i for i in entity_counts.values()],
        }
    )
    # get list of entities for each entity type for tooltip
    data["Ents"] = data["Entity"].apply(
        lambda x: [ent for ent in ents if ent.label_ == x]
    )

    # create altair donut chart
    c = (
        alt.Chart(data)
        .mark_arc(innerRadius=60)
        .encode(
            theta=alt.Theta(field="Count", type="quantitative"),
            color=alt.Color(
                field="Entity",
                type="nominal",
                scale=alt.Scale(
                    domain=[i for i in ent_colors.keys()],
                    range=[i for i in ent_colors.values()],
                ),
            ),
            # tooltip on hover
            tooltip=["Entity", "Count", "Ents"],
        )
    )
    # display donut chart
    st.altair_chart(c, use_container_width=True)
