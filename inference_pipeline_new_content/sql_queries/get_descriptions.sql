SELECT
  url,
  description
FROM `govuk-knowledge-graph.content..description`
INNER JOIN `cpto-content-metadata.content_ner_daily_new.{FILTERED_TABLE}` USING (url)
;
