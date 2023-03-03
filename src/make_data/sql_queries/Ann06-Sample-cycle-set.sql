"""
Script to sample all examples tagged with the specify cycle.
Please change the value for the cycle accordingly. Options: 'a', 'b', 'c', 'd'.
And the annotator - options 1 or 2.
"""
SELECT *
FROM `cpto-content-metadata.phase2_categories.annotation_set_cycles`
WHERE cycle = "a" AND annotator = 2
ORDER BY cat
;
