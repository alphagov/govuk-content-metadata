SELECT
  url,
  title AS text
FROM `govuk-knowledge-graph.content.title`
INNER JOIN `cpto-content-metadata.content_ner_daily_new.{FILTERED_TABLE}` USING (url)
;
