-- This script creates a dataset for annotation. It takes a random sample of 1000 lines for each of the categories in the phase being annotated. It also takes a random sample of 1000 lines from across GOV.UK. These are then ordered according to category type, so models can be trained after each 1000 annotations.

CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.annotation_set` AS (
WITH title_true AS(
SELECT *, "title" as cat FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`
  WHERE contains_title = True ORDER BY RAND() LIMIT 1000
),
role_true AS(
  SELECT *, "role" as cat FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`
  WHERE contains_role = True ORDER BY RAND() LIMIT 1000
),
loc_true AS(
  SELECT *, "loc" as cat FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`
  WHERE contains_loc = True ORDER BY RAND() LIMIT 1000
),
occ_true AS(
  SELECT *, "occupation" as cat FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`
  WHERE contains_occupation = True ORDER BY RAND() LIMIT 1000
),
sector_true AS(
  SELECT *, "sector" as cat FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`
  WHERE contains_sector = True ORDER BY RAND() LIMIT 1000
),
joined_regexp AS(
	  SELECT *, "regexp" as regex_or_rand FROM title_true
	  UNION ALL
	  SELECT *, "regexp" as regex_or_rand FROM role_true
	  UNION ALL
	  SELECT *, "regexp" as regex_or_rand FROM loc_true
	  UNION ALL
	  SELECT * , "regexp" as regex_or_randFROM occ_true
	  UNION ALL
	  SELECT *, "regexp" as regex_or_rand FROM sector_true
	),
rand_samp AS(
  SELECT url, line_number, line, "rand" as regex_or_rand, "rand" as cat FROM `cpto-content-metadata.content_ner.text`
  ORDER BY RAND() LIMIT 1000
)
SELECT
* FROM joined_regexp
UNION ALL
SELECT
* FROM rand_samp
ORDER BY cat
);
