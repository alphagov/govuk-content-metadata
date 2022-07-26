import boto3
import botocore
import os


# need to fix date
DATE = "2022-07-20"
DATE_SHORT = "200722"
CONTENT_S3_BUCKET = "govuk-data-infrastructure-integration"
CONTENT_DIR = f"knowledge-graph/{DATE}"
CONTENT_FILENAME = f"preprocessed_content_store_{DATE_SHORT}.csv.gz"

CONTENT_PATH = os.path.join(CONTENT_DIR, CONTENT_FILENAME)
OUTPUT_CONTENT_PATH = os.path.join(os.getenv("DIR_DATA_RAW"), CONTENT_FILENAME)

# create an STS client object that represents a live connection to the
# STS service
sts_client = boto3.client("sts")


def assume_role_with_mfa(role_arn):

    """
    Assume role with MFA and return credentials
    """

    mfa_otp = input("Enter the MFA code: ")

    assumedRoleObject = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="mysession",
        SerialNumber="arn:aws:iam::622626885786:mfa/alessia.tosi@digital.cabinet-office.gov.uk",
        DurationSeconds=3600,
        TokenCode=mfa_otp,
    )

    # From the response that contains the assumed role, get the temporary
    # credentials that can be used to make subsequent API calls
    return assumedRoleObject["Credentials"]


# Get the cross-account credentials, then use them to create
# an S3 Client and list buckets in the account

creds = assume_role_with_mfa("arn:aws:iam::210287912431:role/govuk-datascienceusers")


# Call the assume_role method of the STSConnection object and pass the role
# ARN and a role session name.

# From the response that contains the assumed role, get the temporary
# credentials that can be used to make subsequent API calls


# Use the temporary credentials that AssumeRole returns to make a
# connection to Amazon S3
s3_resource = boto3.resource(
    "s3",
    aws_access_key_id=creds["AccessKeyId"],
    aws_secret_access_key=creds["SecretAccessKey"],
    aws_session_token=creds["SessionToken"],
)

# Use the Amazon S3 resource object that is now configured with the
# credentials to access your S3 buckets.
for bucket in s3_resource.buckets.all():
    print(bucket.name)


# Download the file
try:
    s3_resource.Bucket(CONTENT_S3_BUCKET).download_file(
        CONTENT_PATH, OUTPUT_CONTENT_PATH
    )
except botocore.exceptions.ClientError as e:
    if e.response["Error"]["Code"] == "404":
        print("The object does not exist.")
    if e.respone["Error"]["Code"] == "400":
        print("Session has expired - Please re-authenticate")
    else:
        raise
