# `src/make_data` folder overview

This folder contains various scripts and functions that are used at various points throughout the project. The purpose of the scripts in these section are always to contribute to the creation of datasets, be it for generating data for annotation, or creating a dataset for another reason. 

There are 4 .sql files that are used for creating an annotation set. These are all prefixed with `Ann-0x...`:

1. `Ann01-Flag_phase2_titles_desc_lines_merged`
This script uses regex strings to identify which seed terms and categories are identified in individual lines across gov.uk content. The 'CREATE' commands should be run sequentially, as they can time out.

2. `Ann02-Create_primary_lower_merge`
This SQL script merges primary tables for each of title, description and lines, and casts the term detected in the line to lower case. This is done in order to count the occurences of terms in a later script.

3. `Ann03-Value_counts`
This SQL Script calculates value counts for each of the phase 2 categories, so users can see how many occurences of seed terms have been calculated across the primary tables. This is 'lower' because we do not want capitalised and lowercase terms calculated separately.

4. `Ann04-Generate_testing_data`
This script creates a dataset for annotation. It takes a random sample of 1000 lines for each of the categories in the phase being annotated. It also takes a random sample of 1000 lines from across GOV.UK. These are then ordered according to category type, so models can be trained after each 1000 annotations.