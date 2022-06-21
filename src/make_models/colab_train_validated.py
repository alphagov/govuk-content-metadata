import argparse
import logging
import os
import sys
import json

from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
from datetime import date
from datasets import load_from_disk, load_metric, ClassLabel, Sequence
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForTokenClassification,
)
from transformers.trainer_utils import get_last_checkpoint

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    # hyperparameters sent by the client are passed as command-line arguments to the script.
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--train_batch_size", type=int, default=16)
    parser.add_argument("--eval_batch_size", type=int, default=16)
    parser.add_argument("--warmup_steps", type=int, default=500)
    parser.add_argument("--model_id", type=str)
    parser.add_argument("--learning_rate", type=str, default=2e-5)
    parser.add_argument("--fp16", type=bool, default=True)

    # Data, model, and output directories
    parser.add_argument("--output_dir", type=str, default=os.environ["SM_MODEL_DIR"])
    parser.add_argument("--n_gpus", type=str, default=os.environ["SM_NUM_GPUS"])
    parser.add_argument(
        "--train_data_dir", type=str, default=os.environ["SM_TRAIN_DATA"]
    )
    parser.add_argument("--test_data_dir", type=str, default=os.environ["SM_TEST_DATA"])
    parser.add_argument(
        "--mapping_file", type=str, default=os.environ["SM_MAPPING_FILE"]
    )
    # parser.add_argument("--training_dir", type=str, default=os.environ["SM_CHANNEL_TRAIN"])
    # parser.add_argument("--test_dir", type=str, default=os.environ["SM_CHANNEL_TEST"])

    args, _ = parser.parse_known_args()

    # Set up logging
    logger = logging.getLogger(__name__)

    logging.basicConfig(
        level=logging.getLevelName("INFO"),
        handlers=[logging.StreamHandler(sys.stdout)],
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # load datasets
    train_dataset = load_from_disk(args.train_data_dir)
    test_dataset = load_from_disk(args.test_data_dir)

    dataset_name = args.train_data_dir.split("/")[-1]
    print("Dataset_name: ", dataset_name)

    logger.info(f" loaded train_dataset length is: {len(train_dataset)}")
    logger.info(f" loaded test_dataset length is: {len(test_dataset)}")

    # load label map as dictionary
    with open(args.mapping_file) as json_file:
        label_map = json.load(json_file)

    # get list of labels (keys from dictionary)
    label_names = list(label_map.keys())
    num_labels = len(label_names)

    train_dataset.features[f"new_label_list_id"] = Sequence(
        feature=ClassLabel(
            num_classes=num_labels, names=label_names, names_file=None, id=None
        ),
        length=-1,
        id=None,
    )
    test_dataset.features[f"new_label_list_id"] = Sequence(
        feature=ClassLabel(
            num_classes=num_labels, names=label_names, names_file=None, id=None
        ),
        length=-1,
        id=None,
    )

    # data tokenisation
    tokenizer = AutoTokenizer.from_pretrained(args.model_id)

    label_all_tokens = True

    def tokenize_and_align_labels(examples):
        tokenized_inputs = tokenizer(
            examples["text_tokens"], truncation=True, is_split_into_words=True
        )

        labels = []
        for i, label in enumerate(examples[f"new_label_list_id"]):
            word_ids = tokenized_inputs.word_ids(
                batch_index=i
            )  # Map tokens to their respective word.
            previous_word_idx = None
            label_ids = []
            for (
                word_idx
            ) in (
                word_ids
            ):  # Set the special tokens to -100. Special tokens have a word id that is None. We set the label to -100 so they are automatically ignored in the loss function.
                if word_idx is None:
                    label_ids.append(-100)
                elif (
                    word_idx != previous_word_idx
                ):  # Only label the first token of a given word.
                    label_ids.append(label[word_idx])
                else:  # For the other tokens in a word, we set the label to either the current label or -100, depending on the label_all_tokens flag.
                    label_ids.append(label[word_idx] if label_all_tokens else -100)
                previous_word_idx = word_idx

            labels.append(label_ids)

        tokenized_inputs["labels"] = labels
        return tokenized_inputs

    tokenized_train_dataset = train_dataset.map(tokenize_and_align_labels, batched=True)
    tokenized_test_dataset = test_dataset.map(tokenize_and_align_labels, batched=True)

    # define metrics
    metric = load_metric("seqeval")

    def compute_metrics(p):
        predictions, labels = p
        predictions = np.argmax(predictions, axis=2)

        # Remove ignored index (special tokens)
        true_predictions = [
            [label_list[p] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [label_list[l] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]

        results = metric.compute(predictions=true_predictions, references=true_labels)

        return {
            "precision": results["overall_precision"],
            "recall": results["overall_recall"],
            "f1": results["overall_f1"],
            "accuracy": results["overall_accuracy"],
        }

    # Prepare model labels - useful in inference API
    label_list = train_dataset.features[f"new_label_list_id"].feature.names
    num_labels = len(label_list)
    id2label = {str(i): label for i, label in enumerate(label_list)}
    label2id = {v: k for k, v in id2label.items()}

    # download model from model hub
    model = AutoModelForTokenClassification.from_pretrained(
        args.model_id, num_labels=num_labels, label2id=label2id, id2label=id2label
    )

    # training
    model_name = args.model_id.split("/")[-1]
    tod_date = date.today().strftime("%d-%m-%Y")
    full_model_name = f"{model_name}-finetuned-ner-govuk-{tod_date}-{dataset_name}"
    out_path = f"{args.output_dir}/{full_model_name}"

    # data collator
    data_collator = DataCollatorForTokenClassification(tokenizer)

    logger.info("***** collated data *****")

    train_args = TrainingArguments(
        output_dir=out_path,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=args.train_batch_size,
        per_device_eval_batch_size=args.eval_batch_size,
        num_train_epochs=args.epochs,
        weight_decay=0.01,
        push_to_hub=False,
    )

    trainer = Trainer(
        model,
        train_args,
        train_dataset=tokenized_train_dataset,
        eval_dataset=tokenized_test_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics,
    )

    trainer.train()
    logger.info("***** training complete *****")

    # save the model to model folder
    model_folder = os.path.join(args.output_dir, full_model_name)
    trainer.save_model(model_folder)
    logger.info("***** model saved *****")

    # make folder in model folder for metrics if doesn't exist
    model_metrics_folder = os.path.join(model_folder, f"Metrics")
    if not os.path.exists(model_metrics_folder):
        os.mkdir(model_metrics_folder)

    # overall results
    print(f"***** Eval results *****")
    eval_result = trainer.evaluate(eval_dataset=tokenized_test_dataset)
    eval_items = eval_result.items()
    eval_list = list(eval_items)
    eval_df = pd.DataFrame(eval_list)
    excel_path = os.path.join(model_metrics_folder, f"overall_results.xlsx")
    eval_df.to_excel(excel_path, sheet_name="overall_results")

    # detailed results
    print(f"***** Detail results *****")
    predictions, labels, _ = trainer.predict(tokenized_test_dataset)
    predictions = np.argmax(predictions, axis=2)
    # Remove ignored index (special tokens)
    true_predictions = [
        [label_list[p] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [label_list[l] for (p, l) in zip(prediction, label) if l != -100]
        for prediction, label in zip(predictions, labels)
    ]
    results = metric.compute(predictions=true_predictions, references=true_labels)
    results_df = pd.DataFrame(results).T
    excel_path = os.path.join(model_metrics_folder, f"detailed_results.xlsx")
    results_df.to_excel(excel_path, sheet_name="detailed_results")

    # confusion matrix
    print(f"***** Confusion Matrix *****")
    true_labels_flat = [item for sublist in true_labels for item in sublist]
    true_preds_flat = [item for sublist in true_predictions for item in sublist]

    confusion_labels = sorted(list(set(true_preds_flat)))

    # with 'O'
    confmat = confusion_matrix(y_true=true_labels_flat, y_pred=true_preds_flat)
    cmplot = ConfusionMatrixDisplay(
        confmat, display_labels=confusion_labels
    )  # , display_labels=label_names[1:]
    fig, ax = plt.subplots(figsize=(15, 15))
    cmplot.plot(ax=ax, cmap="GnBu")
    fig_path = os.path.join(model_metrics_folder, f"confusion_matrix_o.png")
    plt.title("Confusion Matrix (With 'O')")
    plt.savefig(fig_path)

    # without
    confmat_2 = [i[:-1] for i in confmat[:-1]]
    confmat_2 = np.array(confmat_2)
    confusion_labels_no_O = confusion_labels[:-1]
    cmplot = ConfusionMatrixDisplay(confmat_2, display_labels=confusion_labels_no_O)
    fig, ax = plt.subplots(figsize=(15, 15))
    cmplot.plot(ax=ax, cmap="GnBu")
    fig_path = os.path.join(model_metrics_folder, f"confusion_matrix.png")
    plt.title("Confusion Matrix (Without 'O')")
    plt.savefig(fig_path)

    logger.info("***** results complete *****")
