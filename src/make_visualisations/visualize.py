import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import spacy
import visualizer
from config import colors, entity_names, default_text
from util import get_model_metrics

# import displacy

# page config
st.set_page_config(
    page_title="GovNER 2.0",
    page_icon="🧐",
)


# page titles
st.title("Welcome to GovNER 2.0 🧐")
st.write("### Demonstration of NER on GOV.UK page")
st.write(
    "Data Products have developed a model that can detect entities of interest from 'govspeak' in GOV.UK content. \n\n\
    Use the tool below on any GOV.UK url to see how it works."
)

with st.sidebar:
    ModelType = st.selectbox(
        "Choose your model",
        ["Transformer", "Basic"],
        help="At present, you can choose between 2 models (Transformer or Basic) to embed your text. More to come!",
    )

    if ModelType == "Transformer":
        # kw_model = KeyBERT(model=roberta)

        @st.cache(allow_output_mutation=True)
        def load_model():
            return spacy.load("models/mdl_ner_trf_b1_b4/model-best")

        nlp = load_model()

    else:

        @st.cache(allow_output_mutation=True)
        def load_model():
            return spacy.load("models/mark_goppepdm/model-best")

        nlp = load_model()

    # metrics
    metrics = get_model_metrics(nlp)
    st.metric(label="F-Score", value=metrics["model_f"], delta="1st")
    st.metric(label="Precision", value=metrics["model_p"], delta="1st")
    st.metric(label="Recall", value=metrics["model_r"], delta="1st")

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

data = np.random.randint(20, 100, 6)
plt.pie(data)
circle = plt.Circle((0, 0), 0.7, color="white")
p = plt.gcf()
p.gca().add_artist(circle)
plt.show()

st.pyplot(plt)
