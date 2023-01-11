-- This SQL script merges primary tables for each of title, description and lines, and casts the term detected in the line to lower case. This is done in order to count the occurences of terms in a later script.

CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.primarytable_lower_merge` AS

WITH merged_table AS (
  SELECT *, title as line FROM `cpto-content-metadata.phase2_categories.primarytable_titles`
  UNION ALL 
  SELECT *, description as line FROM `cpto-content-metadata.phase2_categories.primarytable_descriptions`
  UNION ALL
  SELECT *, line as line FROM `cpto-content-metadata.phase2_categories.primarytable_lines`
)

SELECT url,
      line_number,
      line,
      contains_title,
      contains_loc,
      contains_role,
      contains_occupation,
      contains_sector,
  (SELECT ARRAY_AGG(CAST(LOWER(item) AS string)) 
    FROM UNNEST(which_title) AS item) AS which_title_l,
  (SELECT ARRAY_AGG(CAST(LOWER(item) AS string)) 
    FROM UNNEST(which_loc) AS item) AS which_loc_l,
  (SELECT ARRAY_AGG(CAST(LOWER(item) AS string)) 
    FROM UNNEST(which_role) AS item) AS which_role_l,
  (SELECT ARRAY_AGG(CAST(LOWER(item) AS string)) 
    FROM UNNEST(which_occupation) AS item) AS which_occupation_l,
  (SELECT ARRAY_AGG(CAST(LOWER(item) AS string)) 
    FROM UNNEST(which_sector) AS item) AS which_sector_l
FROM merged_table
ORDER BY url, line_number;