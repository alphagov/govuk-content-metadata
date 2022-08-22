"""
Script to batch upload the extracted entities to S3, to the folder:
`s3://govuk-data-infrastructure-integration/knowledge-graph-static/entities_intermediate/`


How to run:
python src/make_data/upload_entities_to_s3.py

Requirements:

1. The following environment variables needs to be defined in the `.secrets` files
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_USERNAME`: Your AWS username, usually NAME.SURNAME in your @digital.cabinet.office.gov.uk
- `AWS_GDSUSER_ACCOUNTID`: Account ID for gds-users account
- `AWS_DATASCIENCEUSERS_ACCOUNTID`: Account ID for the datascienceusers role
- `AWS_DATASCIENCEUSERS_NAME`: Full name of the datascience user role

2. Files with extracted entities saved in the local folder: "data/processed/entities"

"""


import os
from tqdm import tqdm
from src.utils.helpers_aws import (
    assume_role_with_mfa,
    temporary_connect_to_s3,
    upload_file_to_s3,
)

# Files info
LOCAL_FOLDER = "data/processed/entities"
S3_BUCKET = "govuk-data-infrastructure-integration"
S3_FOLDER = "knowledge-graph-static/entities_intermediate"

# AWS ARN details
AWS_GDSUSER_ACCOUNTID = os.getenv("AWS_GDSUSER_ACCOUNTID")
AWS_DATASCIENCEUSERS_ACCOUNTID = os.getenv("AWS_DATASCIENCEUSERS_ACCOUNTID")
AWS_DATASCIENCEUSERS_NAME = os.getenv("AWS_DATASCIENCEUSERS_NAME")
AWS_USERNAME = os.getenv("AWS_USERNAME")


with os.scandir(LOCAL_FOLDER) as local_dir:
    if not any(local_dir):
        print(f"Folder {LOCAL_FOLDER} is empty, nothing to upload.")

# Get the cross-account credentials, then use them to create an S3 Client
# Finally download the specified file.
datascienceuser_creds = assume_role_with_mfa(
    username=AWS_USERNAME,
    user_account_id=AWS_GDSUSER_ACCOUNTID,
    role_account_id=AWS_DATASCIENCEUSERS_ACCOUNTID,
    role_name=AWS_DATASCIENCEUSERS_NAME,
)

s3_resource = temporary_connect_to_s3(datascienceuser_creds)

count = 0
for file in tqdm(os.listdir(LOCAL_FOLDER)):
    if file.endswith(".jsonl"):
        try:
            upload_file_to_s3(
                s3_resource=s3_resource,
                file_name=file,
                file_folder=LOCAL_FOLDER,
                s3_bucket=S3_BUCKET,
                s3_folder=S3_FOLDER,
            )
        finally:
            count += 1
print(f"{count} JSONL files successfully uploaded to S3.")
