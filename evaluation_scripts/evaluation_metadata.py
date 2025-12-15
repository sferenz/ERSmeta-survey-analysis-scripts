"""
evaluation_metadata.py

This script analyzes metadata JSON files according to a given schema (ERSmeta) and generates summary statistics
and visualizations. It produces histograms and boxplots for element usage, priority, thematical areas,
and cardinality, and combines all generated figures into a single PDF for easy analysis.

Main Steps:
- Loads metadata schema and all metadata JSON files from the input directory.
- Computes and visualizes the frequency of each metadata element across all sets.
- Aggregates and visualizes statistics by element priority (required, recommended, bonus).
- Aggregates and visualizes statistics by thematical area (e.g., General, Provenance, Quality).
- Analyzes and visualizes the cardinality (number of items) for elements that allow multiple values.
- Combines all generated PDF figures into a single report.

Usage:
    python evaluation_metadata.py --input <metadata_dir> --output_dir <results_dir>

Arguments:
    --input:      Path to the directory containing metadata JSON files (default: current directory).
    --output_dir: Path to the output directory for results (default: "results").

Dependencies:
    - Requires: pandas, os, json, argparse
    - Imports project modules: create_analysis_metadata, print_metadata_figures, compute_metadata_statistics, print_figures

Outputs:
    - PDF and combined PDF files with histograms and boxplots summarizing metadata element usage and structure.
    - A metadata file documenting the analysis run.
"""
import argparse
import os
import json
import pandas as pd

from create_analysis_metadata import *
from print_metadata_figures import *
from compute_metadata_statistics import *
from print_figures import combine_pdfs_in_folder

# Set up argument parser
parser = argparse.ArgumentParser(description="Load and analyze metadata files.")
parser.add_argument(
    "--input",
    type=str,
    default=".",
    help="Path to the metadata files (default: .)"
)
parser.add_argument(
    "--output_dir",
    type=str,
    default="results",
    help="Path to the output directory"
)
args = parser.parse_args()

# Ensure the output directory exists
os.makedirs(args.output_dir, exist_ok=True)

# Call this after parsing args and before/after your analysis
write_metadata_file(
    args.output_dir,
    args.input
)

# Load metadata schema
json_path = "./ersmeta_schema.json" 
with open(json_path, 'r', encoding='utf-8') as f:
    metadata_schema = json.load(f)
element_names = list(metadata_schema['properties'].keys())

# Load all metadata JSON files from the input directory into an array
metadata_files = [
    f for f in os.listdir(args.input)
    if f != 'index.html' and os.path.isfile(os.path.join(args.input, f))
]

metadata_list = []
for filename in metadata_files:
    file_path = os.path.join(args.input, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
        metadata_list.append(metadata)

# Create general histogram of all elements
# Count how many metadata sets have each property
element_counts = {
    prop: sum(prop in metadata for metadata in metadata_list)
    for prop in element_names
}

# Create a DataFrame from the counts
df_element_counts = pd.DataFrame(
    list(element_counts.items()),
    columns=['property', 'count']
)

df_element_counts['priority'] = df_element_counts['property'].apply(get_priority, args=(metadata_schema,))

# element_names = list(metadata_schema['properties'].keys())
element_positions = {name: idx for idx, name in enumerate(element_names)}
max_position = len(element_names) - 1
df_element_counts['position'] = df_element_counts['property'].map(element_positions)
df_element_counts['position'] = df_element_counts['position'].fillna(0).astype(int)

save_element_histogram(
    df_element_counts,
    max_position,
    os.path.join(args.output_dir, 'element_histogram.pdf')
)

# Create aggregated statistics by priority
element_types = {
    'required': metadata_schema['required'],
    'recommended': metadata_schema['recommended'],
}
element_types['bonus'] = [
    elem for elem in element_names
    if elem not in element_types['recommended'] and elem not in element_types['required']
]
# Create a Series with the number of elements for each element type
max_series = pd.Series({name: len(element_list) for name, element_list in element_types.items()})

# Create a DataFrame with the element counts for all element_types
element_type_counts = [
    count_elements_per_metadata(element_list, metadata_list, name)
    for name, element_list in element_types.items()
]

df_element_type_counts = pd.concat(element_type_counts, axis=1)   
save_element_type_boxplots(
    df_element_type_counts, 
    os.path.join(args.output_dir, 'element_priorities.pdf'), 
    max_series=max_series,
    title="Element Count per Metadata Set Categroized in Priority")

# Create aggregated statistics for thematical areas
element_types = {
    'General': get_element_subset(element_names, 'name', 'inLanguage'),
    'GeneralDescription': get_element_subset(element_names, 'abstract', 'copyrightHolder'),
    'Provenance': get_element_subset(element_names, 'dateCreated', 'maintainer'),
    'Usage': get_element_subset(element_names, 'downloadUrl', 'example'),
    'Community': get_element_subset(element_names, 'usedInPublication', 'communityInteractions'),
    'Quality': get_element_subset(element_names, 'review', 'validation'),
    'Interface': get_element_subset(element_names, 'output', 'usedData'),
    'Functionalities': get_element_subset(element_names, 'purpose', 'usedOptimization'),
    'TechnicalRequirements': get_element_subset(element_names, 'typicalHardware', 'fileSize'),
    'MetaMetadata': get_element_subset(element_names, 'metadataVersion', 'sdLicense')
}
# Create a Series with the number of elements for each element type
max_series = pd.Series({name: len(element_list) for name, element_list in element_types.items()})

# Create a DataFrame with the element counts for all element_types
element_type_counts = [
    count_elements_per_metadata(element_list, metadata_list, name)
    for name, element_list in element_types.items()
]

df_element_type_counts = pd.concat(element_type_counts, axis=1)   
save_element_type_boxplots(
    df_element_type_counts, 
    os.path.join(args.output_dir, 'element_thematical_areas.pdf'), 
    max_series=max_series,
    title="Element Count per Metadata Set Categroized in Thematical Areas")    

# Create statistics for all elements with multiple allowed values
elements_with_items = [
    name for name, prop in metadata_schema['properties'].items()
    if 'items' in prop
]

df_items_per_element = count_items_per_element(metadata_list, elements_with_items)
save_element_type_boxplots(
    df_items_per_element, 
    os.path.join(args.output_dir, 'element_cardinality.pdf'), 
    annotate_stats=True, 
    title="Number of items per element",
    xlabel="Items",
    ylabel="Elements")


# Combine all PDFs in the output directory into a single PDF
combine_pdfs_in_folder(
    args.output_dir, f"{args.output_dir}/combined_results.pdf")