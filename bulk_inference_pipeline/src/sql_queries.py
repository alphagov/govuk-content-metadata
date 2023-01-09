import yaml

# cloud
with open("bulk_inference_config.yml", "r") as file:
    config = yaml.safe_load(file)

source_govgraph_project = config["gcp_govgraph"]["project_id"]
source_govgraph_dataset = config["gcp_govgraph"]["bq_content_dataset"]
metadata_project = config["gcp_metadata"]["project_id"]
metadata_dataset = config["gcp_metadata"]["bq_content_dataset"]
metadata_intermediate_table = config["gcp_metadata"]["bq_content_tables"][
    "intermediate_table"
]

intermediate_query = f"""WITH en_locales AS (
  SELECT
    url,
    locale
  FROM `{source_govgraph_project}.{source_govgraph_dataset}.locale`
  WHERE locale='en'
  ),
  live_phases AS (
    SELECT
        url,
        phase
    FROM `{source_govgraph_project}.{source_govgraph_dataset}.phase`
    WHERE phase IN ('live', 'beta')
    ),
    document_types AS (
        SELECT
            url,
            document_type
        FROM `{source_govgraph_project}.{source_govgraph_dataset}.document_type`
        WHERE document_type IS NOT NULL AND document_type NOT IN (
            'business_support_finder',
            'finder',
            'finder_email_signup',
            'gone',
            'licence_finder',
            'need',
            'placeholder',
            'placeholder_ministerial_role',
            'placeholder_person',
            'placeholder_policy_area',
            'placeholder_topical_event',
            'placeholder_world_location_news_page',
            'world_location_news',
            'redirect',
            'special_route')
        )
        SELECT
            u.url,
            dt.document_type,
            pua.public_updated_at
        FROM `{source_govgraph_project}.{source_govgraph_dataset}.url` u
        INNER JOIN en_locales USING (url)
        INNER JOIN live_phases USING (url)
        INNER JOIN document_types dt USING (url)
        LEFT JOIN `{source_govgraph_project}.{source_govgraph_dataset}.public_updated_at` pua USING (url)
        ;
        """

title_query = f"""SELECT
  url,
  title
FROM `{source_govgraph_project}.{source_govgraph_dataset}.title`
INNER JOIN `{metadata_project}.{metadata_dataset}.{metadata_intermediate_table}` USING (url)
;
"""

description_query = f"""SELECT
  url,
  description
FROM `{source_govgraph_project}.{source_govgraph_dataset}.description`
INNER JOIN `{metadata_project}.{metadata_dataset}.{metadata_intermediate_table}` USING (url)
;
"""

text_query = f"""WITH no_extra_whites AS (
  SELECT
    url,
    line_number,
    line as original_line,
    REGEXP_REPLACE(LTRIM(RTRIM(line)), r'\\s+', ' ') as line
    FROM `{source_govgraph_project}.{source_govgraph_dataset}.lines`
    INNER JOIN `{metadata_project}.{metadata_dataset}.{metadata_intermediate_table}` USING (url)
    ),
    extra_info AS (
      SELECT
        url,
        line_number,
        original_line,
        line,
        CHAR_LENGTH(line) AS number_of_chars,
        CHAR_LENGTH(REGEXP_REPLACE( REGEXP_REPLACE(line, ' ', ''), r'([^[:ascii:]]+)', '')) AS number_of_chars_that_are_ascii,
        CHAR_LENGTH(REGEXP_REPLACE(line, r'.,;!?/|()£ ', '')) AS number_of_chars_no_puncs,
      FROM no_extra_whites
      ),
      props_ascii_chars AS (
        SELECT
          url,
          line_number,
          original_line,
          line,
          ROUND(number_of_chars_that_are_ascii / number_of_chars_no_puncs, 4) AS prop_ascii_chars
        FROM extra_info
        )
        SELECT
          url,
          line_number,
          original_line,
          prop_ascii_chars,
          REGEXP_EXTRACT_ALL(line,
            r'(?i:(?:(?:(?:ftp|https?):\\/\\/)(?:www\\.)?|www\\.))(?:[a-zA-Z]+://)?(?:[a-zA-Z0-9-.]+)/{1}([a-zA-Z0-9-./]+)') AS embed_url,
          REGEXP_REPLACE(line, r'(?i:(?:(?:(?:ftp|https?):\\/\\/)(?:www\\.)?|www\\.))(?:[a-zA-Z]+:\\/\\/)?(?:[a-zA-Z0-9-.]+)/{1}([a-zA-Z0-9-./]+)', '') AS line,
        FROM props_ascii_chars
        WHERE prop_ascii_chars >= 0.1
        ORDER BY url, line_number
        ;
        """
