"""
Script to create different sets (cycles), each with equal proportions of entity categories.
"""

CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.annotation_set_cycles` AS

WITH shuffled_data AS (
  SELECT * FROM `cpto-content-metadata.phase2_categories.annotation_set`
  ORDER BY RAND()
),
numbered_shuffled AS (
SELECT *, ROW_NUMBER() OVER(PARTITION BY cat) as idx FROM shuffled_data
)
SELECT *, CASE WHEN idx <= 400 THEN "a"
WHEN 400 < idx AND idx <= 800 THEN "b"
WHEN 800 < idx AND idx <= 1200 THEN "c"
WHEN 1200 < idx AND idx <= 1600 THEN "d"
WHEN 1600 < idx AND idx <= 2000 THEN "e"
END
AS cycle,
IF (MOD(idx, 2 ) = 0, 1, 2) AS annotator
FROM numbered_shuffled;
