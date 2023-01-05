-- This sql script creates/replace two tables:
-- (1) cpto-content-metadata.named_entities.named_entities_all
-- (2) cpto-content-metadata.named_entities.named_entities_counts

-- At the moment, this query is attached to the following schedule
-- found at: https://console.cloud.google.com/bigquery/scheduled-queries/locations/ \
--     us/configs/63d1df30-0000-2629-90c0-001a114d40b2/runs?project=cpto-content-metadata


-- (1) post-extraction cleaning:
-- create a new column containing the lower-case name of the entity instance
-- REMOVE NOISE 1: exclude entity instances that start with non-ascii symbol (e.g., '- hello') and are tagged as ORG
-- REMOVE NOISE 2: exclude entities that consist of a single character
-- REMOVE NOISE 3: exclude entity instances that contain no ascii character at all
-- create url for each unique combination of entity's name and type
-- only keep lines with entities extracted
CREATE OR REPLACE TABLE `cpto-content-metadata.named_entities.named_entities_all` AS

WITH ents_all AS (
SELECT
  url,
  entities[SAFE_OFFSET(0)].name,
  LOWER(entities[SAFE_OFFSET(0)].name) AS name_lower,
  entities[SAFE_OFFSET(0)].type,
  'title' AS part_of_page
FROM `cpto-content-metadata.named_entities_raw.title_1`
WHERE entities[SAFE_OFFSET(0)].name IS NOT null
UNION ALL
SELECT
  url,
  entities[SAFE_OFFSET(0)].name,
  LOWER(entities[SAFE_OFFSET(0)].name) AS name_lower,
  entities[SAFE_OFFSET(0)].type,
  'description' AS part_of_page
FROM `cpto-content-metadata.named_entities_raw.description_1`
WHERE entities[SAFE_OFFSET(0)].name IS NOT null
UNION ALL
SELECT
  url,
  entities[SAFE_OFFSET(0)].name AS name,
  LOWER(entities[SAFE_OFFSET(0)].name) AS name_lower,
  entities[SAFE_OFFSET(0)].type,
  'text' AS part_of_page
FROM `cpto-content-metadata.named_entities_raw.text_1`
WHERE entities[SAFE_OFFSET(0)].name IS NOT null
)
-- REMOVE NOISE 1: exclude entity instances that start with non-ascii symbol (e.g., '- hello') and are tagged as ORG
-- REMOVE NOISE 2: exclude entities that consist of a single character
-- REMOVE NOISE 3: exclude entity instances that contain no ascii character at all
-- create url for each unique combination of entity's name and type
SELECT
  *,
  CONCAT('https://www.gov.uk/named-entity/', REPLACE(name_lower, ' ', '_'), type) AS url_entity_nametype,
FROM ents_all
WHERE (NOT (REGEXP_CONTAINS(name_lower, r"^[^\p{ASCII}]") AND type="ORG")) AND (NOT (REGEXP_CONTAINS(name_lower, r'^[�#£"]') AND type='ORG')) AND (CHAR_LENGTH(name_lower) > 1) AND (ARRAY_LENGTH(REGEXP_EXTRACT_ALL(REPLACE(name_lower, ' ', ''), r"[\p{ASCII}]")) > 0)
ORDER BY url
;


-- (2) aggregate and count
CREATE OR REPLACE TABLE `cpto-content-metadata.named_entities.named_entities_counts` AS

WITH title_counts AS (
SELECT
  url, name_lower, type, url_entity_nametype,
  COUNT(*) OVER (PARTITION BY url, name_lower, type, url_entity_nametype) AS title_count
FROM `cpto-content-metadata.named_entities.named_entities_all`
WHERE part_of_page = "title"
),

description_counts AS (
SELECT
  url, name_lower, type, url_entity_nametype,
  COUNT(*) OVER (PARTITION BY url, name_lower, type, url_entity_nametype) AS description_count
FROM `cpto-content-metadata.named_entities.named_entities_all`
WHERE part_of_page = "description"
),

text_counts AS (
SELECT
  url, name_lower, type, url_entity_nametype,
  COUNT(*) OVER (PARTITION BY url, name_lower, type, url_entity_nametype) AS text_count
FROM `cpto-content-metadata.named_entities.named_entities_all`
WHERE part_of_page = "text"
),

total_counts AS (
  SELECT
  url, name_lower, type, url_entity_nametype,
  COUNT(*) AS total_count
FROM `cpto-content-metadata.named_entities.named_entities_all`
GROUP BY url, name_lower, type, url_entity_nametype
),

combined_counts AS (
SELECT
  *
  FROM title_counts
  FULL JOIN description_counts USING(url, name_lower, type, url_entity_nametype)
  FULL JOIN text_counts USING(url, name_lower, type, url_entity_nametype)
  FULL JOIN total_counts USING(url, name_lower, type, url_entity_nametype)
)

SELECT DISTINCT
 url,
 name_lower,
 type,
 url_entity_nametype,
 IFNULL(title_count, 0) AS title_count,
 IFNULL(description_count, 0) AS description_count,
 IFNULL(text_count, 0) AS text_count,
 IFNULL(total_count, 0) AS total_count,
FROM combined_counts
ORDER BY url
;
