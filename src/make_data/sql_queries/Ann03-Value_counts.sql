-- This SQL Script calculates value counts for each of the phase 2 categories, so users can see how many occurences of seed terms have been calculated across the primary tables. This is 'lower' because we do not want capitalised and lowercase terms calculated separately.

-- ***VALUE COUNTS***
-- title value counts
CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.phase2_titles_counts_lower` AS
SELECT
	  which_title_l,
	  COUNT(which_title_l) AS title_count
	FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`, UNNEST(which_title_l) AS which_title_l
	WHERE contains_title IS true
	GROUP BY which_title_l
	ORDER BY title_count DESC
	;

-- location value counts
CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.phase2_loc_counts_lower` AS
SELECT
	  which_loc_l,
	  COUNT(which_loc_l) AS loc_count
	FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`, UNNEST(which_loc_l) AS which_loc_l
	WHERE contains_loc IS true
	GROUP BY which_loc_l
	ORDER BY loc_count DESC
	;

-- role value counts
CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.phase2_role_counts_lower` AS
SELECT
	  which_role_l,
	  COUNT(which_role_l) AS role_count
	FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`, UNNEST(which_role_l) AS which_role_l
	WHERE contains_role IS true
	GROUP BY which_role_l
	ORDER BY role_count DESC
	;

-- occupation value counts
CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.phase2_occupation_counts_lower` AS
SELECT
	  which_occupation_l,
	  COUNT(which_occupation_l) AS occupation_count
	FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`, UNNEST(which_occupation_l) AS which_occupation_l
	WHERE contains_occupation IS true
	GROUP BY which_occupation_l
	ORDER BY occupation_count DESC
	;

-- sector value counts
CREATE OR REPLACE TABLE `cpto-content-metadata.phase2_categories.phase2_sector_counts_lower` AS
SELECT
	  which_sector_l,
	  COUNT(which_sector_l) AS sector_count
	FROM `cpto-content-metadata.phase2_categories.primarytable_lower_merge`, UNNEST(which_sector_l) AS which_sector_l
	WHERE contains_sector IS true
	GROUP BY which_sector_l
	ORDER BY sector_count DESC
	;
