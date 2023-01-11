-- This SQL Script calculates value counts for each of the phase 2 categories, so users can see how many occurences of seed terms have been calculated across the primary tables. This is 'lower' because we do not want capitalised and lowercase terms calculated separately.

-- ***VALUE COUNTS***
-- title value counts
CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.phase2_titles_counts_lower` AS
WITH categories as (SELECT * FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`)
SELECT unnest_which_title_l, COUNT(unnest_which_title_l) as title_count
FROM categories, UNNEST(categories.which_title_l) as unnest_which_title_l
WHERE (contains_title IS true)
GROUP BY unnest_which_title_l
ORDER BY title_count DESC;

-- location value counts
CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.phase2_loc_counts_lower` AS
WITH categories as (SELECT * FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`)
SELECT unnest_which_loc_l, COUNT(unnest_which_loc_l) as loc_count
FROM categories, UNNEST(categories.which_loc_l) as unnest_which_loc_l
WHERE (contains_loc IS true)
GROUP BY unnest_which_loc_l
ORDER BY loc_count DESC;

-- role value counts
CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.phase2_role_counts_lower` AS
WITH categories as (SELECT * FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`)
SELECT unnest_which_role_l, COUNT(unnest_which_role_l) as role_count
FROM categories, UNNEST(categories.which_role_l) as unnest_which_role_l
WHERE (contains_role IS true)
GROUP BY unnest_which_role_l
ORDER BY role_count DESC;

-- occupation value counts
CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.phase2_occupation_counts_lower` AS
WITH categories as (SELECT * FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`)
SELECT unnest_which_occupation_l, COUNT(unnest_which_occupation_l) as occupation_count
FROM categories, UNNEST(categories.which_occupation_l) as unnest_which_occupation_l
WHERE (contains_occupation IS true)
GROUP BY unnest_which_occupation_l
ORDER BY occupation_count DESC;

-- sector value counts
CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.phase2_sector_counts_lower` AS
WITH categories as (SELECT * FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`)
SELECT unnest_which_sector_l, COUNT(unnest_which_sector_l) as sector_count
FROM categories, UNNEST(categories.which_sector_l) as unnest_which_sector_l
WHERE (contains_sector IS true)
GROUP BY unnest_which_sector_l
ORDER BY sector_count DESC;
