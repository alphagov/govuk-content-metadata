# `src/make_data` folder overview

This folder contains various scripts and functions that are used at various points throughout the project. The purpose of the scripts in these section are always to contribute to the creation of datasets, be it for generating data for annotation, or creating a dataset for another reason.

## `src/make_data/sql_queries`

There are 4 .sql files that are used for creating an annotation set. These are all prefixed with `Ann-0x...`:

1. `sql_queries/Ann01-Flag_phase2_titles_desc_lines_merged`
This script uses regex strings to identify which seed terms and categories are identified in individual lines across gov.uk content. The 'CREATE' commands should be run sequentially, as they can time out. 'Seed terms' are a collection of words of phrases that are predetermined and manually curated by the project team, and

2. `sql_queries/Ann02-Create_primary_lower_merge`
Primary tables contain lines across GOV.UK with flags to indicate if a line in question contains a certain type of entity, and and what enitity it is that is contained. This SQL script merges primary tables for each of title, description and lines, and casts the term detected in the line to lower case. This is done in order to count the occurences of terms in a later script.

3. `sql_queries/Ann03-Value_counts`
This SQL Script calculates value counts for each of the phase 2 categories, so users can see how many occurences of seed terms have been calculated across the primary tables. In this context, the value count is the amount of times a particular entity has occured across GOV.UK; this can be titles, descriptions, or main text. This is 'lower' because we do not want capitalised and lowercase terms calculated separately.

4. `sql_queries/Ann04-Generate_testing_data`
This script creates a dataset for annotation. It takes a random sample of 1000 lines for each of the categories in the phase being annotated where a seed term has been flagged in the `primary_table` (step 2). It also takes a random sample of 1000 lines from across GOV.UK. These are then ordered according to category type, so models can be trained after each 1000 annotations.

In addition, the following files allow the users to select the training sets:

5. `sql_queries/Ann05-Stratify-annotation-set.sql`
Scripts that creates different sets (cycles), each with equal proportions of entity categories.

6. `sql_queries/Ann06-Sample-cycle-set.sql`
Script to sample all examples tagged with a specified cycle.

Bonus script:

7. `sql_queries/Ann07-Create-sample-for-event-category.sql`
Script to create a training set with texts that are likley to contain EVENT entity instances.

### Dependencies

All these scripts and generated tables are dependent on the `cpto-content-metadata.phase2_categories` dataset.
