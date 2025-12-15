"""
evaluation_survey.py

This script processes and analyzes survey data from a CSV file related to the ERSmeta project.
It generates descriptive statistics, visualizations, and exports for survey responses, including
demographics, prior experience, dropout reasons, usability (SUS), behavioral intention, extraction
quality, feature requests, and free-text feedback. The script supports filtering participants based
on metadata experience and produces publication-ready figures and summary files.

Main Steps:
- Loads survey data from a CSV file.
- Optionally filters participants based on metadata experience or survey completion.
- Generates and saves:
    - Demographics and prior experience diagrams (pie charts, bar charts, text/PDF exports)
    - Dropout/completion reason diagrams
    - System Usability Scale (SUS) statistics and boxplots
    - Behavioral intention, extraction quality, and feature request boxplots
    - Aggregated and free-text response exports
- Combines all generated PDF figures into a single report for easy analysis.

Arguments:
    --input: Path to the survey CSV file (default: "your_large_file.csv")
    --output_dir: Path to the output directory for results (default: "results")
    --exclude_missing_metadata_experience: Exclude participants without metadata experience
    --only_missing_metadata_experience: Include only participants without metadata experience

Dependencies:
    - pandas, argparse, os, json, datetime, subprocess
    - Project modules: write_column, compute_column_statistics, print_figures,
      create_analysis_metadata, create_survey_statistics

Outputs:
    - PDF and text files with figures and free-text responses in the output directory
    - A combined PDF report of all figures
    - A metadata file documenting the analysis run

Usage Example:
    python evaluation_survey.py --input survey.csv --output_dir results --exclude_missing_metadata_experience
"""

import pandas as pd
import argparse
import os
import json
import datetime
import subprocess

from write_column import *
from compute_column_statistics import *
from print_figures import *
from create_analysis_metadata import *
from create_survey_statistics import *

# Set up argument parser
parser = argparse.ArgumentParser(description="Load and analyze a CSV file.")
parser.add_argument(
    "--input",
    type=str,
    default="your_large_file.csv",
    help="Path to the CSV file (default: your_large_file.csv)"
)
parser.add_argument(
    "--output_dir",
    type=str,
    default="results",
    help="Path to the output directory"
)
parser.add_argument(
    "--exclude_missing_metadata_experience",
    action="store_true",
    help="Indicate that persons without metadata experience should be excluded from the analysis"
)
parser.add_argument(
    "--only_missing_metadata_experience",
    action="store_true",
    help="Indicate that only persons without metadata experience should be included in the analysis"
)
args = parser.parse_args()

# Ensure the output directory exists
os.makedirs(args.output_dir, exist_ok=True)

# Call this after parsing args and before/after your analysis
write_metadata_file(
    args.output_dir,
    args.input,
    args.exclude_missing_metadata_experience,
    args.only_missing_metadata_experience
)

# Use the 'dtype' argument to optimize memory usage if you know column types
# Use 'usecols' to load only specific columns if you don't need all columns
evaluation_df = pd.read_csv(args.input, low_memory=False)

# Demographics
generate_demographics_diagrams(evaluation_df,f"{args.output_dir}/A_"," (all survey participants)")

# Prior experience
generate_prior_experience_diagrams(evaluation_df,f"{args.output_dir}/A_"," (all survey participants)")

# Create a figure with the number of participants over the different steps
generate_dropout_reasons_diagrams(evaluation_df,f"{args.output_dir}/B_","")


# Remove excluded rows
if args.exclude_missing_metadata_experience:
    evaluation_df = evaluation_df[
        evaluation_df['G02Q06'].notna() & (evaluation_df['G02Q06'] != 'I am not familiar with metadata schemas.')
    ]
if args.only_missing_metadata_experience:
    evaluation_df = evaluation_df[
        (evaluation_df['G02Q06'] == 'I am not familiar with metadata schemas.')
    ]

# Exclude incomplete surveys
evaluation_df = evaluation_df[(evaluation_df['lastpage'] == 12)]
    

# Demographics
generate_demographics_diagrams(evaluation_df,f"{args.output_dir}/C_"," (Full survey participants)")

# Prior experience
generate_prior_experience_diagrams(evaluation_df,f"{args.output_dir}/C_"," (Full survey participants)")

# SMECS
## SUS
columns_description = {
    'G04Q11[SQ002]':'I think that I would like to use this system frequently',
    'G04Q11[SQ003]':'I found the system unnecessarily complex',
    'G04Q11[SQ004]':'I thought the system was easy to use',
    'G04Q11[SQ005]':'I think that I would need the support of a technical person to be able to use this system',
    'G04Q11[SQ006]':'I found the various functions in this system were well integrated',
    'G04Q11[SQ007]':'I thought there was too much inconsistency in this system',
    'G04Q11[SQ008]':'I would imagine that most people would learn to use this system very quickly',
    'G04Q11[SQ009]':'I found the system very cumbersome to use',
    'G04Q11[SQ010]':'I felt very confident using the system',
    'G04Q11[SQ011]':'I needed to learn a lot of things before I could get going with this system'
}
columns_positive_counting = { 
    'G04Q11[SQ002]':True,
    'G04Q11[SQ003]':False,
    'G04Q11[SQ004]':True,
    'G04Q11[SQ005]':False,
    'G04Q11[SQ006]':True,
    'G04Q11[SQ007]':False,
    'G04Q11[SQ008]':True,
    'G04Q11[SQ009]':False,
    'G04Q11[SQ010]':True,
    'G04Q11[SQ011]':False
}
columns = columns_description.keys()
file_name = "Q11_SUS"
title = "Q11: System Usability Scale (SUS) for SMECS"
generate_pdf_with_boxplots(evaluation_df, columns, f"{args.output_dir}/{file_name}_stats.pdf", columns_description, title, columns_positive_counting)
sus_data = calculate_sus(evaluation_df, columns_positive_counting)

generate_pdf_sus(sus_data, f"{args.output_dir}/{file_name}_sus.pdf")


## Behavioral Intention to use SMECS
boxplots_metadata = {}
boxplots_metadata['Q12_Intention']= {
    "columns_description": {
        'G04Q12[SQ002]':'I intend to use SMECS for another energy research software',
        'G04Q12[SQ003]':'I will recommend SMECS to my colleagues',
        'G04Q12[SQ004]':'I have positive perceptions about SMECS'
    },
    "columns_positive_counting": { 
        'G04Q12[SQ002]':True,
        'G04Q12[SQ003]':True,
        'G04Q12[SQ004]':True
    }, 
    "title": "Q12: Behavioral Intention to use SMECS"
}

## Quality of Extraction
boxplots_metadata['Q13_Extraction_Quality']={
    "columns_description": {
        'G01Q13[SQ002]':'The quality of the extracted metadata was high',
        'G01Q13[SQ003]':'I had no problem with the quality of the extracted metadata',
        'G01Q13[SQ004]':'Using the metadata extraction enhances the effectiveness of creating metadata',
        'G01Q13[SQ005]':'I find the system to be useful to extract metadata'
    },
    "columns_positive_counting": { 
        'G01Q13[SQ002]':True,
        'G01Q13[SQ003]':True,
        'G01Q13[SQ004]':True,
        'G01Q13[SQ005]':True
    },
    "title": "Q13: Extraction Quality of SMECS (Output Quality + Perceived usefulness)"
}

## Additional features
columns_description = {
    'G01Q14[SQ002]':'Extracting additional information for my software from provided links to literature (e.g., software paper or other related paper) would have been helpful for me',
    'G01Q14[SQ003]':'Extracting additional information from package repositories (e.g., pypi) would have been helpful for me',
    'G01Q14[SQ004]':'I would like to have an option to export the metadata directly to my repository',
    'G01Q14[SQ005]':'I would like to have an option to directly publish the metadata in a software registry'
}
columns = columns_description.keys()
file_name = "Q14_Features"
title = "Q14: Possible Features of SMECS"
generate_pdf_with_boxplots(evaluation_df, columns, f"{args.output_dir}/{file_name}_stats.pdf", columns_description, title)


## Free text
columns_descriptions = {"G01Q16":"What did you dislike most about SMECS?",
               "G04Q15":"What did you like most about SMECS?",
               "G01Q17":"Please provide any additional comments or suggestions for improving SMECS."}
columns = columns_descriptions.keys()

write_column_to_txt(evaluation_df, columns, f"{args.output_dir}/Q16_free_text_values.txt", columns_descriptions)
write_column_to_pdf(evaluation_df, columns, f"{args.output_dir}/Q16_free_text_values.pdf", columns_descriptions)

# ERSmeta
## Amount of elements
boxplots_metadata['Q18_Amount_of_Elements']={
    "columns_description": {
        'G05Q18[SQ002]':'I find the overall number of elements useful to describe my research software',
        'G05Q18[SQ003]':'The amount of elements is too high',
        'G05Q18[SQ004]':'The categorization of elements into three categories is helpful',
        'G05Q18[SQ005]':'The number of mandatory elements is useful for me',
        'G05Q18[SQ006]':'The number of recommended elements is useful for me.'
    },
    "columns_positive_counting": { 
        'G05Q18[SQ002]':True,
        'G05Q18[SQ003]':False,
        'G05Q18[SQ004]':True,
        'G05Q18[SQ005]':True,
        'G05Q18[SQ006]':True
    },
    "title": "Q18: Impression on the Amount of Elements"
}

## Usefulness of elements
boxplots_metadata['Q19_Usefulness_of_Elements']={
    "columns_description": {
        'G05Q19[SQ002]':'Using the metadata schema to describe my research software would enable me to enrich my software with metadata more quickly.',
        'G05Q19[SQ003]':'I find the metadata schema useful to describe my research software',
        'G05Q19[SQ004]':'I find it easy to use the metadata schema to describe my research software in the way I want',
        'G05Q19[SQ005]':'I find the metadata schema to be flexible to use it',
        'G05Q19[SQ006]':'I missed certain elements in the metadata schema to describe my research software',
        'G05Q19[SQ007]':'The quality of the created metadata is high',
        'G05Q19[SQ008]':'I have no problem with the quality of the created metadata',
        'G05Q19[SQ009]':'Assuming I have access to the metadata schema, I intend to use it to describe my software',
        'G05Q19[SQ010]':'Given that I have access to the metadata schema, I predict that I would use it to describe my software'
    },
    "columns_positive_counting": { 
        'G05Q19[SQ002]':True,
        'G05Q19[SQ003]':True,
        'G05Q19[SQ004]':True,
        'G05Q19[SQ005]':True,
        'G05Q19[SQ006]':False,
        'G05Q19[SQ007]':True,
        'G05Q19[SQ008]':True,
        'G05Q19[SQ009]':True,
        'G05Q19[SQ010]':True
    },
    "title": "Q19: Usefulness of Elements (perceived usefulness, perceived ease of use, output quality, behavioral intention)"
}

## Descriptions of the elements
boxplots_metadata['Q20_Descriptions_of_Elements']={
    "columns_description": {
        'G01Q20[SQ002]':'I find the descriptions useful for creating the metadata',
        'G01Q20[SQ003]':'Using the descriptions enables me to describe my research software more quickly',
        'G01Q20[SQ004]':'I thought there was too much inconsistency in the metadata elements',
        'G01Q20[SQ005]':'Given the descriptions, it is easy for me to create metadata for my research software',
        'G01Q20[SQ006]':'I could create metadata for my energy research software if there was no one around to tell me what to do as I go',
        'G01Q20[SQ007]':'I could create metadata for my energy research software if I could call someone for help if I got stuck',
        'G01Q20[SQ008]':'I could create metadata for my energy research software if I had a lot of time to complete the metadata',
        'G01Q20[SQ009]':'I could create metadata for my energy research software if I had just the built-in help facility for assistance'
    },
    "columns_positive_counting": { 
        'G01Q20[SQ002]':True,
        'G01Q20[SQ003]':True,
        'G01Q20[SQ004]':False,
        'G01Q20[SQ005]':True,
        'G01Q20[SQ006]':True,
        'G01Q20[SQ007]':True,
        'G01Q20[SQ008]':True,
        'G01Q20[SQ009]':True
    },
    "title": "Q20: Descriptions of Elements"
}

## Usefulness of Value Vocabularies
boxplots_metadata['Q21_Usefulness_of_Value_Vocabularies']={
    "columns_description": {
        'G05Q21[SQ002]':'I find the provided lists to be flexible to use it to describe my research software',
        'G05Q21[SQ003]':'I find it easy to use provided lists to describe my research software in the way I want',
        'G05Q21[SQ004]':'Using the provided lists to describe my research software would enable me to enrich my software with metadata more quickly.',
        'G05Q21[SQ005]':'I find the provided lists useful to describe my research software'
    },
    "columns_positive_counting": { 
        'G05Q21[SQ002]':True,
        'G05Q21[SQ003]':True,
        'G05Q21[SQ004]':True,
        'G05Q21[SQ005]':True
    },
    "title": "Q21: Usefulness of Value Vocabularies (Perceived Ease of Use, Perceived Usefulness)"
}

## Free text #G05Q22, G12Q23, G01Q24, G01Q25, G01Q26
columns_descriptions = {"G05Q22":"Which certain elements do you miss in the metadata schema?",
               "G12Q23":"​​​​​​Which additional information on your software would you have liked to provide?",
               "G01Q24":"What did you like most about the metadata schema?",
               "G01Q25":"What did you dislike most about the metadata schema?",
               "G01Q26":"Please provide any additional comments or suggestions for improving the metadata schema."}    
columns = columns_descriptions.keys()

write_column_to_txt(evaluation_df, columns, f"{args.output_dir}/Q22_Q26_free_text_values.txt", columns_descriptions)
write_column_to_pdf(evaluation_df, columns, f"{args.output_dir}/Q22_Q26_free_text_values.pdf", columns_descriptions)

# Create all boxplots for the columns
for file_name, data in boxplots_metadata.items():
    columns = data["columns_description"].keys()
    generate_pdf_with_boxplots(
        evaluation_df,
        columns,
        f"{args.output_dir}/{file_name}_stats.pdf",
        data["columns_description"],
        data["title"],
        data["columns_positive_counting"]
    )
    aggregated_data = calculate_mean_values(
        evaluation_df, data["columns_positive_counting"]
    )
    generate_pdf_with_boxplot_for_series(
        aggregated_data,
        f"{args.output_dir}/{file_name}_aggregated.pdf",
        description="",
        overall_title=data["title"]
    )

# Combine all PDFs in the output directory into a single PDF
combine_pdfs_in_folder(
    args.output_dir, f"{args.output_dir}/combined_results.pdf")