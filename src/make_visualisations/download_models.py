import os
from google.cloud import storage

# Instantiates a client
# You must have personal access to GCP bucket, or service account credentials saved as ['GOOGLE_APPLICATION_CREDENTIALS'] as a secret
storage_client = storage.Client()
# The name for the new bucket
bucket_name = "cpto-content-metadata"
# Creates the new bucket


def download_file_from_bucket(blob_name, file_path, bucket_name):
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(blob_name)
        with open(file_path, "wb") as f:
            storage_client.download_blob_to_file(blob, f)
        return True
    except Exception as e:
        print(e)
        return False


def list_contents_of_bucket(bucket_name, folder):
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder)
    return [blob.name for blob in blobs]


def replicate_folder_structure(bucket_name, folder):
    contents = list_contents_of_bucket(bucket_name, folder)
    dirnames = {os.path.dirname(i) for i in contents}
    for i in dirnames:
        # print(os.path.join(str(os.getcwd()), i))
        if not os.path.exists(os.path.join(os.getcwd(), i)):
            os.makedirs(os.path.join(os.getcwd(), i))


def download_files_from_bucket(bucket_name, folder):
    # files = list_contents_of_bucket(bucket_name, folder)
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder)
    blob_names = [i.name for i in blobs]
    for blob_name in blob_names:
        print(blob_name)
        download_file_from_bucket(
            blob_name=blob_name,
            file_path=os.path.join(os.getcwd(), blob_name),
            bucket_name=bucket_name,
        )
        print(f"{blob_name} downloaded!")


if __name__ == "__main__":

    replicate_folder_structure(
        bucket_name=bucket_name, folder="models/mdl_ner_trf_b1_b4/model-best"
    )

    download_files_from_bucket(
        bucket_name=bucket_name, folder="models/mdl_ner_trf_b1_b4/model-best"
    )
