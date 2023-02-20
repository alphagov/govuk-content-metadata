import typer
import srsly
from pathlib import Path
from collections import Counter
import spacy
from typing import List, Tuple, Optional
import numpy as np
import random
from iteration_utilities import unique_everseen


def count_labels_per_class_from_jsonl(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False)
) -> List[Tuple[str, int]]:
    """
    Counts the number of labels per category/class in a JSONL-prodigy formatted file of sample annotations.

    Args:
        input_path: full path to the JSONL-file
    Returns:
        the count of labels in each category in ascending order, as a list of tuples.

    Example:
        [('LOC', 157), ('SECTOR', 196), ('FAC', 220)]
    """
    counts = Counter()
    for eg in srsly.read_jsonl(input_path):
        if eg["answer"] != "accept":
            continue
        for span in eg.get("spans", []):
            counts[span["label"]] += 1
    return list(reversed(counts.most_common()))


def count_labels_per_class(file: List[dict] = None) -> List[Tuple[str, int]]:
    """
    Counts the number of labels per category/class in a JSONL-prodigy formatted file of sample annotations.

    Args:
        file: a jsonl object, loaded in memory
    Returns:
        the count of labels in each category in ascending order, as a list of tuples.

    Example:
        [('LOC', 157), ('SECTOR', 196), ('FAC', 220)]
    """
    counts = Counter()
    for eg in file:
        for span in eg.get("spans", []):
            counts[span["label"]] += 1
    return list(reversed(counts.most_common()))


def stratify_train_test(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False),
    folder_output_path: str = typer.Argument(...),
    test_size: Optional[float] = typer.Argument(0.2),
):
    """
    Splits multi-label samples based on their number of categories.
    Each sample may contain several tags from different categories. The
    process of splitting starts from the categories with the smallest number of samples to make sure their ratio is saved
    because they have small numbers of samples.

    Args:
        input_path: path to the JSONL prodigy-formatted file containing entity annotations
        folder_output_path: path to the folder where to save the data_train.jsonl and data_test.jsonl
        test_size: size of the test set as a proportion (default: 0.2)

    Returns:
        None
        Saves the data_train.jsonl and data_test.jsonl to the specified folder_output_path.
    """

    print(f"test/train split ratio: {test_size}")
    ordered_counts = count_labels_per_class_from_jsonl(input_path=input_path)

    print(f"labels per entity category: {ordered_counts}")

    # stratify starts from the category/class with the lowest number of samples
    spacy.util.fix_random_seed(0)
    samples_gen = srsly.read_jsonl(input_path)  # generator
    # exclude samples with no tags and randomly shuffle the list of samples
    samples = [eg for eg in samples_gen if eg["answer"] == "accept"]
    random.shuffle(samples)
    # n_original_samples = len(samples)

    test_samples = []
    train_samples = []

    for cat_idx in range(0, len(ordered_counts)):
        print(f"{cat_idx} - Processing entity category: {ordered_counts[cat_idx][0]}")
        print(f"start of iteration: length of samples is {len(samples)}")
        class_subsamples = [
            eg
            for eg in samples
            for span in eg["spans"]
            if span.get("label") == ordered_counts[cat_idx][0]
        ]
        # deduplicate
        # # since if a sample contains more than one annotation for the same category,
        # # it will appear more than once
        class_subsamples = list(unique_everseen(class_subsamples.copy()))
        print(
            f"number of unique samples containing {ordered_counts[cat_idx][0]} labels: {len(class_subsamples)}"
        )

        class_n = len(class_subsamples)
        class_n_test = int(np.ceil(class_n * test_size))
        class_n_train = int(class_n - class_n_test)

        class_test = class_subsamples[:class_n_test]
        class_train = class_subsamples[class_n_test:]

        assert len(class_test) == class_n_test
        assert len(class_train) == class_n_train

        test_samples.extend(class_test)
        train_samples.extend(class_train)

        # update samples, removing the samples just extracted for class 0
        samples = [eg for eg in samples.copy() if eg not in class_subsamples]

        print(f"end of iteration: length of samples is {len(samples)}")

    # also split those samples without categories labels
    print("Processing Samples - remainder")
    reminder_n = len(samples)
    reminder_n_test = int(np.ceil(reminder_n * test_size))
    reminder_n_train = int(reminder_n - reminder_n_test)

    reminder_test = samples[:reminder_n_test]
    reminder_train = samples[reminder_n_test:]

    assert len(reminder_test) == reminder_n_test
    assert len(reminder_train) == reminder_n_train

    test_samples.extend(reminder_test)
    train_samples.extend(reminder_train)

    random.shuffle(test_samples)
    random.shuffle(train_samples)

    srsly.write_jsonl(Path(folder_output_path, "data_train.jsonl"), train_samples)
    srsly.write_jsonl(Path(folder_output_path, "data_test.jsonl"), test_samples)
    print("Processed completed.")
    print(
        f"Train set \n- size {len(train_samples)}; \n- labels: {count_labels_per_class(train_samples)}"
    )
    print(
        f"Test set \n- size {len(test_samples)}; \n- labels: {count_labels_per_class(test_samples)}"
    )


if __name__ == "__main__":
    typer.run(stratify_train_test)
