# Commonly used Prodigy Commands

### data-to-spacy

Link: https://prodi.gy/docs/recipes#data-to-spacy

Task: Create a .spacy docbin with training and test data. Efficient for training models and metadata for training a pipeline.

Combine multiple datasets, merge annotations on the same examples and output training and evaluation data in spaCy’s binary .spacy format, which you can use with spacy train. The command takes an output directory and generates all data required to train a pipeline with spaCy, including the config and pre-generated labels data to speed up the training process. This recipe will merge annotations for the different pipeline components and outputs a combined training corpus. If an example is only present in one dataset type, its annotations for the other components will be missing values. It’s recommended to use the  review recipe on the different annotation types first to resolve conflicts properly.
