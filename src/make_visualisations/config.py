# this is a config file which controls some of the variables used in src.make_visualisations.visualise.py

colors = {
    "FORM": "#79dd6f",
    "GPE": "#00ffcc",
    "MONEY": "#e4f60b",
    "ORG": "#ff00ee",
    "PERSON": "#ffdd00",
    "DATE": "#fcf6d3",
    "POSTCODE": "#f9b750",
    "EMAIL": "#FADBEA",
    "PHONE": "#aaff00",
}

entity_names = [k for (k, _) in colors.items()]

# default_text = """Tom Read is CEO of GDS. He has been in the role since March 2021. GDS has a budget of £80 million for the 2021-2022 year. Whilst Mr Read has a background in MoJ, GDS has many employees who have worked for tech firms like Google and Apple, but also legal firms like Knockheart Mickleson. Prospective employees should get in touch with recruitment@digital.cabinet-office.gov.uk or call 0203 451 9000, they may ask to see your P45 or similar documents. Our office is located at 10 Whitechapel High Street, London E1 8QS."""  # noqa
default_text = """Abisọla Fatokun is an enterprise digital transformation specialist with extensive public sector experience. He previously worked with the UK Government Digital Service’s Service Standards team ensuring that standards are met, and with the Ministry of Justice Digital & Technology team where he worked with senior leaders at the Legal Aid Agency, helping them to change to a service-led approach. Abisọla has also worked at KPMG, Accenture and BSkyB (now Sky). In 1999, Abisọla founded the first web development company in Nigeria, which he later sold."""  # noqa
