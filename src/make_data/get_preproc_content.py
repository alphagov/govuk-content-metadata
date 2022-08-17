"""
Script to download the preprocessed content store from S3.

It takes two arguments:
- d: [OPTIONAL, default is yestreday] "YYYY-MM-DD" date for which to download the copy of the content store
- u: username for your AWS account, usually name.surname of your gds email address.

How to run:
python src/make_data/get_preproc_content.py -d "2022-07-20" -u "paul.smith"

Requirements:
The following environment variables needs to be defined in the `.secrets` files
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_GDSUSER_ACCOUNTID`: Account ID for gds-users account
- `AWS_DATASCIENCEUSERS_ACCOUNTID`: Account ID for the datascienceusers role
- `AWS_DATASCIENCEUSERS_NAME`: Full name of the datascience user role
"""


import os
from datetime import date, timedelta
from src.utils.helpers_aws import (
    assume_role_with_mfa,
    temporary_connect_to_s3,
    download_file_from_s3,
)
from src.utils.helpers_formatting import shorten_date_format


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Run src.make_data.get_preproc_content"
    )

    # Define the positional arguments we want to get from the user
    parser.add_argument(
        "--username",
        "-u",
        type=str,
        action="store",
        dest="username",
        required=True,
        help="specify your AWS username, usually <name.surname>",
    )

    parser.add_argument(
        "--date",
        "-d",
        type=str,
        action="store",
        dest="date",
        required=False,
        help="specify the date 'YYYY-MM-DD' of the preprocessed content store copy; default is yesterday",
    )

    parsed_args = parser.parse_args()

    # Default is yesterday unless superseded
    if parsed_args.date:
        TARGET_DATE = parsed_args.date
    else:
        today = date.today()
        TARGET_DATE = today - timedelta(days=1)

    TARGET_DATE_SHORT = shorten_date_format(TARGET_DATE)

    print(TARGET_DATE)
    print(TARGET_DATE_SHORT)

    # AWS S3 info
    CONTENT_S3_BUCKET = "govuk-data-infrastructure-integration"
    CONTENT_DIR = f"knowledge-graph/{TARGET_DATE}"
    CONTENT_FILENAME = f"preprocessed_content_store_{TARGET_DATE_SHORT}.csv.gz"
    CONTENT_PATH = os.path.join(CONTENT_DIR, CONTENT_FILENAME)
    print(CONTENT_PATH)

    # Outputs
    OUTPUT_CONTENT_PATH = os.path.join(os.getenv("DIR_DATA_RAW"), CONTENT_FILENAME)

    # AWS ARN details
    AWS_GDSUSER_ACCOUNTID = os.getenv("AWS_GDSUSER_ACCOUNTID")
    AWS_DATASCIENCEUSERS_ACCOUNTID = os.getenv("AWS_DATASCIENCEUSERS_ACCOUNTID")
    AWS_DATASCIENCEUSERS_NAME = os.getenv("AWS_DATASCIENCEUSERS_NAME")

    if os.path.isfile(OUTPUT_CONTENT_PATH):
        print(f"File {OUTPUT_CONTENT_PATH} already exists.")
        exit()

    # Get the cross-account credentials, then use them to create
    # an S3 Client and list buckets in the account.
    # Finally download the specified file.
    datascienceuser_creds = assume_role_with_mfa(
        username=parsed_args.username,
        user_account_id=AWS_GDSUSER_ACCOUNTID,
        role_account_id=AWS_DATASCIENCEUSERS_ACCOUNTID,
        role_name=AWS_DATASCIENCEUSERS_NAME,
    )

    s3_resource = temporary_connect_to_s3(datascienceuser_creds)

    download_file_from_s3(
        s3_resource=s3_resource,
        s3_bucket=CONTENT_S3_BUCKET,
        file_key=CONTENT_PATH,
        output_filepath=OUTPUT_CONTENT_PATH,
    )

    print(f"File {CONTENT_PATH} downloaded successfully.")
