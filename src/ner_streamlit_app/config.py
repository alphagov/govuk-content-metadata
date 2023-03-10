# this is a config file which controls some of the variables used in src.make_visualisations.visualise.py

colors = {
    "ORG": "#98fb98",
    "PERSON": "#b0e0e6",
    "GPE": "#ffdab9",
    "TITLE": "#ffb6c1",
    "ROLE": "#d8ac28",
    "LOC": "#ccffff",
    "FORM": "#79dd6f",
    "MONEY": "#e4f60b",
    "DATE": "#ffd700",
    "POSTCODE": "#f9b750",
    "EMAIL": "#38ad04",
    "PHONE": "#aaff00",
    "OCCUPATION": "#d0c2ef",
    "FAC": "#f58a07",
    "EVENT":"#0099ff"
}

entity_names = [k for (k, _) in colors.items()]

default_text = """Rishi Sunak became Prime Minister on 25 October 2022. He was previously appointed Chancellor of the Exchequer from 13 February 2020 to 5 July 2022. He was Chief Secretary to the Treasury from 24 July 2019 to 13 February 2020, and Parliamentary Under Secretary of State at the Ministry of Housing, Communities and Local Government from 9 January 2018 to 24 July 2019. Rishi went to Winchester College and studied Politics, Philosophy and Economics at Oxford University. He was also a Fulbright Scholar at Stanford University (USA) where he studied for his MBA. Rishi was elected Conservative MP for Richmond (Yorks) in May 2015 and served as a Parliamentary Private Secretary at the Department for Business, Energy and Industrial Strategy from June 2017 until his ministerial appointment."""  # noqa
