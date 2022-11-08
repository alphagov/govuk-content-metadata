import os
from google.cloud import storage
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s")


def instantiate_storage_client():
    """Instantiates a client.You must have personal access to GCP bucket, or service account
    credentials saved as ['GOOGLE_APPLICATION_CREDENTIALS'] as a secret
    """
    storage_client = storage.Client()
    return storage_client


def download_file_from_bucket(blob_name, file_path, bucket_name, storage_client):
    """Download a file from a GCP bucket.

    :param blob_name: Blob name
    :type blob_name: file
    :param file_path: Output file path
    :type file_path: str
    :param bucket_name: Bucket name
    :type bucket_name: str
    :return: True/False
    :rtype: Bool
    """
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        with open(file_path, "wb") as f:
            storage_client.download_blob_to_file(blob, f)
        return True
    except Exception as e:
        logging.warning(e)
        return False


def list_contents_of_bucket(bucket_name, folder, storage_client):
    """List the contents of a bucket.

    :param bucket_name: Bucket name.
    :type bucket_name: str
    :param folder: Bucket folder
    :type folder: str
    :return: List of blobs in bucket/folder
    :rtype: list
    """
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder)
    return [blob.name for blob in blobs]


def replicate_folder_structure(bucket_name, folder, storage_client):
    """Replicate the structure of a GCP Bucket/folder

    :param bucket_name: Bucket name
    :type bucket_name: str
    :param folder: Bucket folder
    :type folder: str
    """
    contents = list_contents_of_bucket(bucket_name, folder, storage_client)
    dirnames = {os.path.dirname(i) for i in contents}
    for i in dirnames:
        if not os.path.exists(os.path.join(os.getcwd(), i)):
            os.makedirs(os.path.join(os.getcwd(), i))


def download_files_from_bucket(bucket_name, folder, storage_client):
    """Download files from a bucket.

    :param bucket_name: Bucket name
    :type bucket_name: str
    :param folder: Bucket folder
    :type folder: str
    """
    logging.info("DOWNLOADING MODEL FILES.")
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder)
    blob_names = [i.name for i in blobs]
    for blob_name in blob_names:
        download_file_from_bucket(
            blob_name=blob_name,
            file_path=os.path.join(os.getcwd(), blob_name),
            bucket_name=bucket_name,
            storage_client=storage_client,
        )
        logging.info(f"{blob_name} downloaded.")


if __name__ == "__main__":

    storage_client = instantiate_storage_client()
    bucket_name = "cpto-content-metadata"

    replicate_folder_structure(
        bucket_name=bucket_name,
        folder="models/mdl_ner_trf_b1_b4/model-best",
        storage_client=storage_client,
    )

    download_files_from_bucket(
        bucket_name=bucket_name,
        folder="models/mdl_ner_trf_b1_b4/model-best",
        storage_client=storage_client,
    )
