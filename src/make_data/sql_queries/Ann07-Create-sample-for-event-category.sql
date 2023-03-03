"""
Script to create a training set with texts that are likley to contain EVENT entity instances.
"""

DECLARE event_regex STRING DEFAULT r"(?i)tragic|traumatic|momentous|celebrat|commemorat|attendant|^host|take place|took place|taken place|workshop|seminar|conference|summit|festival|exhibition|^war$|celebration|olympic|anniversary|commemoration|jubilee|earthquake|volcano|hurricane"
;

CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.primarytable_events` AS

WITH events_table AS (
SELECT
  url,
  line_number,
  line,
  REGEXP_EXTRACT_ALL(line, event_regex) as event_cat
FROM `cpto-content-metadata.content_ner.text`
WHERE REGEXP_CONTAINS(line, event_regex)
),

deduplicated_lines AS (
  SELECT
    url,
    line_number,
    line,
    event_cat,
    ROW_NUMBER()
            OVER (PARTITION BY line)
            row_number
  FROM events_table
),

shuffled_data AS (
  SELECT
    url,
    line_number,
    line,
    event_cat
  FROM deduplicated_lines, UNNEST(event_cat) AS event_cat
  WHERE row_number = 1
  ORDER BY RAND()
)

SELECT
  *,
  ROW_NUMBER() OVER(PARTITION BY event_cat) as idx
FROM shuffled_data
;


CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.events_set_cycles` AS

WITH set_cycles AS (
SELECT
  url,
  line_number,
  event_cat,
  line,
  CASE WHEN idx <= 30 THEN "a"
  WHEN 30 < idx AND idx <= 60 THEN "b"
  WHEN 60 < idx AND idx <= 90 THEN "c"
  END
  AS cycle
FROM `cpto-content-metadata.phase2_categories.primarytable_events`
)

SELECT *
FROM set_cycles
WHERE cycle IS NOT NULL
ORDER BY cycle
;
