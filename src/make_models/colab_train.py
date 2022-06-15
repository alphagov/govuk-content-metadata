import argparse
import logging
import os
import sys

import numpy as np
import pandas as pd
from datetime import date
from datasets import load_from_disk, load_metric, ClassLabel, Sequence
from transformers import AutoModelForTokenClassification, AutoTokenizer, Trainer, TrainingArguments, DataCollatorForTokenClassification
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
    parser.add_argument("--output_data_dir", type=str, default=os.environ["SM_OUTPUT_DATA_DIR"])
    parser.add_argument("--output_dir", type=str, default=os.environ["SM_MODEL_DIR"])
    parser.add_argument("--n_gpus", type=str, default=os.environ["SM_NUM_GPUS"])
    parser.add_argument("--data_dir", type=str, default=os.environ["SM_CHANNEL_DATA"])
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
    datasets = load_from_disk(args.data_dir)

    logger.info(f" loaded train_dataset length is: {len(datasets['train'])}")
    logger.info(f" loaded test_dataset length is: {len(datasets['test'])}")

    label_map = {"O": 0,
             "I-CONTACT": 1,
             "I-DATE": 2,
             "I-EVENT": 3,
             "I-FINANCE": 4,
             "I-FORM": 5,
             "I-LOC": 6,
             "I-MISC": 7,
             "I-MONEY": 8,
             "I-ORG": 9,
             "I-PER": 10,
             "I-SCHEME": 11,
             "I-STATE": 12}
    
    labels = ['O', 'I-CONTACT', 'I-DATE', 'I-EVENT', 'I-FINANCE', 'I-FORM', 'I-LOC', 'I-MISC', 'I-MONEY', 'I-ORG', 'I-PER', 'I-SCHEME', 'I-STATE']

    datasets['train'].features[f"new_label_list_id"] = Sequence(feature=ClassLabel(num_classes=13, names=labels, names_file=None, id=None), length=-1, id=None)
    datasets['test'].features[f"new_label_list_id"] = Sequence(feature=ClassLabel(num_classes=13, names=labels, names_file=None, id=None), length=-1, id=None)

    #data tokenisation
    tokenizer = AutoTokenizer.from_pretrained(args.model_id)

    label_all_tokens = True

    def tokenize_and_align_labels(examples):
        tokenized_inputs = tokenizer(examples["text_token"], truncation=True, is_split_into_words=True)

        labels = []
        for i, label in enumerate(examples[f"new_label_list_id"]):
            word_ids = tokenized_inputs.word_ids(batch_index=i) # Map tokens to their respective word.
            previous_word_idx = None
            label_ids = []
            for word_idx in word_ids:  # Set the special tokens to -100. Special tokens have a word id that is None. We set the label to -100 so they are automatically ignored in the loss function.
                if word_idx is None:
                    label_ids.append(-100)
                elif word_idx != previous_word_idx: # Only label the first token of a given word.
                    label_ids.append(label[word_idx])
                else:                   # For the other tokens in a word, we set the label to either the current label or -100, depending on the label_all_tokens flag.
                    label_ids.append(label[word_idx] if label_all_tokens else -100)
                previous_word_idx = word_idx

            labels.append(label_ids)

        tokenized_inputs["labels"] = labels
        return tokenized_inputs

    tokenized_datasets = datasets.map(tokenize_and_align_labels, batched=True)

    # define metrics
    metric = load_metric("seqeval")

    def compute_metrics(p):
        predictions, labels = p
        predictions = np.argmax(predictions, axis=2)

        # Remove ignored index (special tokens)
        true_predictions = [[label_list[p] for (p, l) in zip(prediction, label) if l != -100] for prediction, label in zip(predictions, labels)]
        true_labels = [[label_list[l] for (p, l) in zip(prediction, label) if l != -100]for prediction, label in zip(predictions, labels)]

        results = metric.compute(predictions=true_predictions, references=true_labels)
        
        return {
            "precision": results["overall_precision"],
            "recall": results["overall_recall"],
            "f1": results["overall_f1"],
            "accuracy": results["overall_accuracy"],
        }

    # Prepare model labels - useful in inference API
    label_list = datasets["train"].features[f"new_label_list_id"].feature.names
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
    full_model_name = f"{model_name}-finetuned-ner-govuk-{tod_date}"
    out_path = f"{args.output_dir}/{full_model_name}"

    # data collator
    data_collator = DataCollatorForTokenClassification(tokenizer)

    logger.info("***** collated data *****")

    train_args = TrainingArguments(
        output_dir=out_path,
        evaluation_strategy = "epoch",
        learning_rate=2e-5,
        per_device_train_batch_size=args.train_batch_size,
        per_device_eval_batch_size=args.eval_batch_size,
        num_train_epochs=3,
        weight_decay=0.01,
        push_to_hub=False,
    )

    trainer = Trainer(
        model,
        train_args,
        train_dataset=tokenized_datasets["train"],
        eval_dataset=tokenized_datasets["test"],
        data_collator=data_collator,
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )

    trainer.train()

    # get training metrics
    predictions, labels, _ = trainer.predict(tokenized_datasets["test"])
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
    excel_path = os.path.join(args.output_data_dir, f"{full_model_name}_eval_results_overtall.xlsx")
    results_df.to_excel(excel_path, sheet_name=full_model_name)

    # evaluate model
    eval_result = trainer.evaluate(eval_dataset=tokenized_datasets['test'])

    # writes eval result to file which can be accessed later
    with open(os.path.join(args.output_data_dir, f"{full_model_name}_eval_results.txt"), "w") as writer:
        print(f"***** Eval results *****")
        for key, value in sorted(eval_result.items()):
            writer.write(f"{key} = {value}\n")
            print(f"{key} = {value}\n")

    # Saves the model to os.environ["SM_MODEL_DIR"] to make sure checkpointing works
    trainer.save_model(os.path.join(os.environ["SM_MODEL_DIR"],full_model_name))