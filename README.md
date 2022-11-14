# `govuk-content-metadata`

Project work related to extracting metdadata from gov.uk content.

```{warning}
Where this documentation refers to the root folder we mean where this README.md is
located.
```

## Getting started

To start using this project, [first make sure your system meets its
requirements](#requirements).

To be added.

### Requirements

```{note} Requirements for contributors
[Contributors have some additional requirements][contributing]!
```

- Python 3.9+ installed
- a `.secrets` file with the [required secrets and
  credentials](#required-secrets-and-credentials)
- [load environment variables][docs-loading-environment-variables] from `.envrc`

To install the Python requirements and pre-commit hooks, open your terminal and enter:

```shell
make requirements
```

or, alternatively, to only install the necessary Python packages using pip:

```shell
pip install -r requirements.txt
```

## Required secrets and credentials

To run this project, [you need a `.secrets` file with secrets/credentials as
environmental variables][docs-loading-environment-variables-secrets]. The
secrets/credentials should have the following environment variable name(s):

| Secret/credential | Environment variable name | Description                                |
|-------------------|---------------------------|--------------------------------------------|
| Prodigy License   | `PRODIGY_LICENSE`         | Digit code                                 |

Once you've added, [load these environment variables using
`.envrc`][docs-loading-environment-variables].

## Licence

Unless stated otherwise, the codebase is released under the MIT License. This covers
both the codebase and any sample code in the documentation. The documentation is ©
Crown copyright and available under the terms of the Open Government 3.0 licence.

# Data Version Control (DVC)

[DVC](dvc.org) is used in this project for version control of data and models.

Requirements:
- You must have read and write access to the [project GCP repository](gs://cpto-content-metadata)
- DVC installed with `pip install 'dvc[gs]'`
- Authenticated to used GCloud `gcloud auth application-default login`

The project uses two DVC remotes; for data and models, respectively.

To run:

1. Pull the latest models DVC
  ```shell
  dvc pull -r cpto-ner-dvc-models
  ```
2. Pull the latest training data DVC
  ```shell
  dvc pull -r cpto-ner-dvc-data
  ```

This should populate your local model and data folders from remote storage on GCP.

To commit/push the most recent data and models following updates. Use
```bash
dvc push```
and
```bash
dvc pull```
in place above.

For more information, visit [Syncing Data to GCP Storage Buckets](https://iterative.ai/blog/using-gcp-remotes-in-dvc)

# Inference pipeline [local machine]

To use a trained Spacy NER model to extract Named Entities from GOV.UK content:
- Ensure you meet the [AWS Requirements](#aws-requirements) below.
- You will be asked for your AWS account MFA code, so have it ready!
- Follow the instructions in [src/make_data/infer_entities.sh][infer-entities-sh] to know how to specify optional arguments.

Example: to run the bash script with default values for the optional arguments and extract entities from all the `"titles"` of yesterday's GOV.UK pages using a pre-trained model saved in `models/mdl_ner_trf_b1_b4/model-best`, from the project root directory run

```shell
bash src/make_data/infer_entities.sh -p "title" -m "models/mdl_ner_trf_b1_b4/model-best"
```

## AWS Requirements

1. AWS Access; see https://docs.publishing.service.gov.uk/manual/get-started.html#8-get-aws-access on how to create your AWS user account, and create an access key ID and secret access key.

2. STS Permission to AssumeRole with MFA for the [`govuk-datascienceusers` AWS IAM Role][ds-role] (ask on #data-engineering Slack channel)

3. `aws cli` installed; it should have gotten installed as part of step 1. To verify, in your terminal run:
```shell
which aws
aws --version
```
If it is not available, please [follow the official installation instructions][awscli-install].

4. Configure `aws cli`. In your terminal, run:
```shell
aws configure
```
and follow the prompts (N.B. you will be asked to provide your access key ID and secret access key).

Your credentials should have now been added to the `~/.aws/credentials` file, under `[default]`.

5. Create a profile for the `govuk-datascienceusers` Role in your `~/.aws/config`. If the file does not exist, you'll need to create it. In your `~/.aws/config` file, add:

```
[profile govuk-datascience]
source_profile = default
role_arn = arn:aws:iam::<ROLE ACCOUNT NUM>:role/govuk-datascienceusers
mfa_serial = arn:aws:iam::<YOUR USER ACCOUNT NUMBER>:mfa/<YOUR NAME>.<YOUR SURNAME>@digital.cabinet-office.gov.uk
```

substituting the correct values for `<ROLE ACCOUNT NUM>`, `<YOUR USER ACCOUNT NUMBER>`, `<YOUR NAME>` and `<YOUR SURNAME>`.

You can now assume the `govuk-datascienceusers` role and its permissions to interact with AWS S3 by adding
`--profile govuk-datascience` at the end of your `aws cli` commands.

For instance:
```shell
aws s3 ls --profile govuk-datascience
```

6. You are good to go and infer entities!

[infer-entities-sh]: ./src/make_data/infer_entities.sh
[ds-role]: https://us-east-1.console.aws.amazon.com/iamv2/home?region=eu-west-1#/roles/details/govuk-datascienceusers?section=permissions
[awscli-install]: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
