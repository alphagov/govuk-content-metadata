import spacy
import visualizer
import pandas as pd
import altair as alt
import streamlit as st
from collections import Counter
from config import colors, entity_names, default_text
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

        nlp = load_model(model_path="./models/mdl_ner_trf_b1_b4/model-best")

    # displacy metric for loaded model in sidebar
    metrics = get_model_metrics(nlp)
    st.metric(label="F-Score", value=metrics["model_f"], delta="1st")
    st.metric(label="Precision", value=metrics["model_p"], delta="1st")
    st.metric(label="Recall", value=metrics["model_r"], delta="1st")

    ents_metrics = get_model_ents_metrics(nlp)
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
        doc = [nlp(text_area)]

    if input_type == "Custom GOV.UK URL":
        text_input = st.text_input(
            "Insert GOV.UK URL",
            value="https://www.gov.uk/government/people/elizabeth-truss",
        )
        text = url_get_sents(text_input)
        text = " ".join(text)
        doc = [nlp(text)]

    if input_type == "Random GOV.UK URL":

        text = ""
        doc = [nlp(text)]

        if st.button("Generate Random GOV.UK URL"):
            text = url_get_sents("https://www.gov.uk/random")
            text = " ".join(text)
            doc = [nlp(text)]

# visualisations
col1, col2 = st.columns([2, 1])
with col1:

    # ner visualisations
    visualizer.visualize_ner(
        doc,
        labels=entity_names,
        show_table=False,
        displacy_options={
            "colors": colors,
            "kb_url_template": "https://www.wikidata.org/wiki/{}",
        },
        title=None,
        manual=False,
    )

with col2:
    # entity and label counts
    ents = [list(i.ents) for i in doc][0]
    labels = [e.label_ for e in ents]
    entity_counts = Counter(labels)
    data = pd.DataFrame(
        {
            "Entity": [i for i in entity_counts.keys()],
            "Count": [i for i in entity_counts.values()],
        }
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
                    domain=[i for i in colors.keys()],
                    range=[i for i in colors.values()],
                ),
            ),
            tooltip=["Entity", "Count"],
        )
    )
    st.altair_chart(c, use_container_width=True)
