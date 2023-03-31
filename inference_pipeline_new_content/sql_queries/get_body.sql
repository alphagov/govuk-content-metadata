WITH no_extra_whites AS (
  SELECT
    url,
    line_number,
    line as original_line,
    REGEXP_REPLACE(LTRIM(RTRIM(line)), r'\\s+', ' ') as line
    FROM `govuk-knowledge-graph.content.lines`
    INNER JOIN `cpto-content-metadata.content_ner_daily_new.{FILTERED_TABLE}` USING (url)
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
          REGEXP_REPLACE(line, r'(?i:(?:(?:(?:ftp|https?):\\/\\/)(?:www\\.)?|www\\.))(?:[a-zA-Z]+:\\/\\/)?(?:[a-zA-Z0-9-.]+)/{1}([a-zA-Z0-9-./]+)', '') AS line,
          line_number,
          original_line,
          prop_ascii_chars,
          REGEXP_EXTRACT_ALL(line,
            r'(?i:(?:(?:(?:ftp|https?):\\/\\/)(?:www\\.)?|www\\.))(?:[a-zA-Z]+://)?(?:[a-zA-Z0-9-.]+)/{1}([a-zA-Z0-9-./]+)') AS embed_url,
        FROM props_ascii_chars
        WHERE prop_ascii_chars >= 0.1
        ORDER BY url, line_number
        ;
