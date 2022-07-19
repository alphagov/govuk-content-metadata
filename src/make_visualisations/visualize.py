# This script builds and runs a streamlit web-app to allow interrogation of NER outputs

# imports
import streamlit as st
import pandas as pd
import altair as alt
import spacy
import visualizer
from config import colors, entity_names, default_text
from util import get_model_metrics
from collections import Counter


# page configuration
st.set_page_config(
    page_title="GovNER 2.0",
    page_icon="🧐",
)


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
        ["Transformer", "Basic"],
        help="At present, you can choose between 2 models (Transformer or Basic) to embed your text. More to come!",
    )

    if ModelType == "Transformer":
        # load transformer model and cache
        @st.cache(allow_output_mutation=True)
        def load_model():
            return spacy.load("models/mdl_ner_trf_b1_b4/model-best")

        nlp = load_model()

    else:
        # load 'basic' model and cache
        @st.cache(allow_output_mutation=True)
        def load_model():
            return spacy.load("models/mark_goppepdm/model-best")

        nlp = load_model()

    # displacy metric for loaded model in sidebar
    metrics = get_model_metrics(nlp)
    st.metric(label="F-Score", value=metrics["model_f"], delta="1st")
    st.metric(label="Precision", value=metrics["model_p"], delta="1st")
    st.metric(label="Recall", value=metrics["model_r"], delta="1st")


# text input and processing
text = st.text_area("Insert text for NER here", value=default_text)
doc = [nlp(text)]

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

c = (
    alt.Chart(data)
    .mark_arc(innerRadius=75)
    .encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(
            field="Entity",
            type="nominal",
            scale=alt.Scale(
                domain=[i for i in colors.keys()], range=[i for i in colors.values()]
            ),
        ),
        tooltip=["Entity", "Count"],
    )
)

st.altair_chart(c, use_container_width=True)
