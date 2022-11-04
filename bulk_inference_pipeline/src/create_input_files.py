from google.cloud import bigquery


def write_query(
    client: bigquery.Client,
    sql_query: str,
    dest_project: str,
    dest_dataset: str,
    dest_table: str,
):
    """"""
    destination = f"{dest_project}.{dest_dataset}.{dest_table}"
    job_config = bigquery.QueryJobConfig(
        destination=destination, write_disposition="WRITE_TRUNCATE"
    )

    # Start the query, passing in the extra configuration.
    query_job = client.query(sql_query, job_config=job_config)  # Make an API request.
    # Wait for the job to complete.

    # print(f"Query results loaded to the table {destination}")
    return query_job.result()


if __name__ == "__main__":  # noqa: C901

    import yaml

    from src import sql_queries

    with open("bulk_inference_config.yml", "r") as file:
        config = yaml.safe_load(file)

    metadata_project = config["gcp_metadata"]["project_id"]
    metadata_dataset = config["gcp_metadata"]["bq_content_dataset"]
    metadata_intermediate_table = config["gcp_metadata"]["bq_content_tables"][
        "intermediate_table"
    ]

    # Construct a BigQuery client object.
    client = bigquery.Client()

    # intermediate table
    # TODO: uncomment when ready to run whole pipeline ($$$)
    write_query(
        client=client,
        sql_query=sql_queries.intermediate_query,
        dest_project=metadata_project,
        dest_dataset=metadata_dataset,
        dest_table=metadata_intermediate_table,
    )

    # title
    write_query(
        client=client,
        sql_query=sql_queries.title_query,
        dest_project=metadata_project,
        dest_dataset=metadata_dataset,
        dest_table="title",
    )

    # description
    write_query(
        client=client,
        sql_query=sql_queries.description_query,
        dest_project=metadata_project,
        dest_dataset=metadata_dataset,
        dest_table="description",
    )

    # text
    write_query(
        client=client,
        sql_query=sql_queries.text_query,
        dest_project=metadata_project,
        dest_dataset=metadata_dataset,
        dest_table="text",
    )
