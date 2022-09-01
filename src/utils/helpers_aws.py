"""
Utility functions to access an S3 bucket to downlaod and upload files,
using the AWS SDK for Python boto3.
"""


import os
import boto3
import botocore
import tqdm


def assume_role_with_mfa(username, user_account_id, role_account_id, role_name):

    """
    Assume role (e.g., govuk-datascienceusers) with MFA and return the temporary cross-account credentials.

    Args:
        username: the username in the your personal AWS user account, usually <name>.<surname> as in your @digital.cabinet-office.gov.uk email.
        user_account_id: Account ID of the IAM corresponding to the username
        role_account_id: Account ID of the role to be assume
        role_name: name of the cross-accounts role to be assumed

    Returns:
        The assumed role's temporary credentials that can be used to make subsequent API calls.
    """

    # Create an STS client object, representing a live connection to the STS service
    sts_client = boto3.client("sts")
    # ARN of the role we want to assume
    role_arn = f"arn:aws:iam::{role_account_id}:role/{role_name}"

    MFA_OPT = input("Enter the MFA code: ")

    # Call the assume_role method of the STSConnection object and pass the role ARN and a role session name.
    assumedRoleObject = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="AccessS3Metadata",
        SerialNumber=f"arn:aws:iam::{user_account_id}:mfa/{username}@digital.cabinet-office.gov.uk",
        DurationSeconds=3600,
        TokenCode=MFA_OPT,
    )

    # From the response that contains the assumed role, get the temporary credentials
    return assumedRoleObject["Credentials"]


def temporary_connect_to_s3(temp_creds):
    """
    Uses the temporary credentials that AssumeRole returns to make a connection to Amazon S3.

    Args:
        temp_creds: temporary credentials generated by assume_datascienceusers_role_with_mfa().

    Returns:
        An Amazon S3 resource object configured to have access to S3 buckets accessible to the assumed role.
    """

    s3_resource = boto3.resource(
        "s3",
        aws_access_key_id=temp_creds["AccessKeyId"],
        aws_secret_access_key=temp_creds["SecretAccessKey"],
        aws_session_token=temp_creds["SessionToken"],
    )
    return s3_resource


def download_file_from_s3(s3_resource, s3_bucket, file_key, output_filepath):
    """
    Downloads the file from the S3 bucket folder.

    Args:
        s3_resource: an Amazon S3 resource object configured to have access to S3 buckets
        s3_bucket: name of the S3 bucket (e.g., "govuk-data-infrastructure-integration")
        file_key: name of the file to be downloaded, including folder name (e.g., "knowledge-graph/2022-08-10/myfile.csv")
        output_filepath: full path of the downloaded file

    Returns:
        The downloaded file in the specified location
    """

    object_size = s3_resource.Object(s3_bucket, file_key).content_length

    try:
        with tqdm.tqdm(total=object_size, unit="B", unit_scale=True) as pbar:
            s3_resource.Bucket(s3_bucket).download_file(
                file_key,
                output_filepath,
                Callback=lambda bytes_transferred: pbar.update(bytes_transferred),
            )
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "404":
            print("The object does not exist.")
        if e.response["Error"]["Code"] == "400":
            print("Session has expired - Please re-authenticate")
        else:
            raise


def upload_file_to_s3(
    s3_resource, file_name, file_folder, s3_bucket, s3_folder, object_name=None
):
    """Upload a file to an S3 bucket

    Args:
        s3_resource: An Amazon S3 resource object configured to have access to S3 buckets
        file_name: Name of the file to upload
        file_folder: Path to the file to upload
        s3_bucket: Name of S3 bucket to upload to
        s3_folder: Name of the bucket folder to upload to
        object_name: S3 object name; if not specified then file_name is used

    Returns:
        True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.join(s3_folder, file_name)
    else:
        object_name = os.path.join(s3_folder, object_name)

    file_name_full = os.path.join(file_folder, file_name)

    # Upload the file
    try:
        s3_resource.meta.client.upload_file(
            Filename=file_name_full, Bucket=s3_bucket, Key=object_name
        )
    except botocore.exceptions.ClientError as e:
        print(e)
        return False
    return True
