"""
create_analysis_metadata.py

This module provides utilities for generating and writing metadata about the analysis process.
It records information about the input data, code version, and the analysis run itself,
and saves this information as a JSON metadata file for reproducibility and provenance tracking.

Functions:
- write_metadata_file: Write a metadata JSON file with input, code, and run information.
"""

import os
import json
import datetime
import subprocess

def write_metadata_file(
    output_dir: str,
    input_file: str,
    exclude_missing_metadata_experience: bool = False,
    code_dir: str = ".",
    metadata_filename: str = "metadata.json"
) -> None:
    """
    Writes a metadata file containing information about the analysis run, including:
      - Input file path and last modification date
      - Whether exclusion of missing metadata experience was applied
      - Current code commit hash (if in a git repository)
      - Metadata file creation date

    Args:
        output_dir (str): Directory where the metadata file will be written.
        input_file (str): Path to the input CSV file used for analysis.
        exclude_missing_metadata_experience (bool, optional): Whether exclusion of participants
            with missing metadata experience was applied. Default is False.
        code_dir (str, optional): Directory of the code repository (used to get git commit hash).
            Default is current directory.
        metadata_filename (str, optional): Name of the metadata file to write. Default is "metadata.json".

    Notes:
        - The function attempts to retrieve the last modification time of the input file.
        - The function attempts to retrieve the current git commit hash from the code directory.
        - If either retrieval fails, the value "unknown" is used.
        - The metadata file is written in UTF-8 encoded JSON format with indentation for readability.

    Example:
        write_metadata_file(
            output_dir="results",
            input_file="survey_data.csv",
            exclude_missing_metadata_experience=True,
            code_dir=".",
            metadata_filename="run_metadata.json"
        )
    """
    # Input variables
    metadata = {
        "input_file": input_file,
        "exclude_missing_metadata_experience": exclude_missing_metadata_experience,
    }

    # Input file creation date (last modification time)
    try:
        input_file_stat = os.stat(input_file)
        input_file_creation = datetime.datetime.fromtimestamp(input_file_stat.st_mtime).isoformat()
    except Exception:
        input_file_creation = "unknown"
    metadata["input_file_last_modified"] = input_file_creation

    # Code commit number (git)
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=code_dir, stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
    except Exception:
        commit = "unknown"
    metadata["code_commit"] = commit

    # Metadata file creation date
    metadata["metadata_creation_date"] = datetime.datetime.now().isoformat()

    # Write metadata to file
    metadata_path = os.path.join(output_dir, metadata_filename)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)