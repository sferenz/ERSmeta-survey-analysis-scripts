"""
write_column.py

This module provides utility functions for exporting column values from a pandas DataFrame
to plain text and PDF files. It is designed for use in survey and metadata analysis pipelines
where free-text or categorical responses need to be exported for qualitative analysis.

Main Features:
- Export values from one or more DataFrame columns to a text file, with line wrapping and headings.
- Export values from one or more DataFrame columns to a paginated PDF file, formatted for readability.
- Skips missing (NaN) values and supports custom column descriptions for headings.
- Output is formatted for easy inclusion in reports or further manual analysis.

Functions:
- write_column_to_txt: Write column values to a plain text file, with line wrapping and headings.
- write_column_to_pdf: Write column values to a paginated PDF file, with line wrapping and headings.

Assumptions and Notes:
- Each column's values are preceded by a heading (description or column name).
- Long entries are wrapped for readability; each value is listed as a bullet point.
- All columns are written sequentially in the output file.
- PDF output uses a monospace font and A4 page size for compatibility with academic documents.

Dependencies:
- pandas
- matplotlib (for PDF export)
- textwrap (for line wrapping)
"""
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import textwrap
from typing import List, Dict, Tuple

def write_column_to_txt(
    df: pd.DataFrame,
    column_names: List[str],
    output_file: str,
    column_descriptions: Dict[str, str],
    max_line_length: int = 100
) -> None:
    """
    Writes every value from the specified columns of the DataFrame to a text file, one per line.
    Skips NaN values and line-breaks long entries for readability.
    Each column's values are preceded by its description as a heading.
    All columns are written directly after each other.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        column_names (list of str): The names of the columns to write.
        output_file (str): The path to the output text file.
        column_descriptions (dict): Dictionary mapping column names to descriptions.
        max_line_length (int): Maximum number of characters per line before breaking (default: 100).

    Output:
        - A text file where each column's values are listed under a heading, with each value as a bullet point.
        - Long values are wrapped for readability.
        - Blank lines separate columns.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for column_name in column_names:
            description = column_descriptions.get(column_name, column_name)
            f.write(f"{description}:\n")
            values = [str(val) for val in df[column_name] if not pd.isna(val)]
            for val in values:
                wrapped = textwrap.wrap(val, width=max_line_length) or ['']
                if wrapped:
                    f.write(f"- {wrapped[0]}\n")
                    for cont_line in wrapped[1:]:
                        f.write(f"  {cont_line}\n")
                else:
                    f.write("-\n")
            f.write("\n")  # Add a blank line after each column for separation

def write_column_to_pdf(
    df: pd.DataFrame,
    column_names: List[str],
    output_file: str,
    column_descriptions: Dict[str, str],
    max_line_length: int = 90
) -> None:
    """
    Writes every value from the specified columns of the DataFrame to a paginated PDF file, one per line.
    Skips NaN values and line-breaks long entries for readability.
    Each column's values are preceded by its description as a heading.
    All columns are written directly after each other.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        column_names (list of str): The names of the columns to write.
        output_file (str): The path to the output PDF file.
        column_descriptions (dict): Dictionary mapping column names to descriptions.
        max_line_length (int): Maximum number of characters per line before breaking (default: 90).

    Output:
        - A PDF file where each column's values are listed under a heading, with each value as a bullet point.
        - Long values are wrapped for readability.
        - Blank lines separate columns.
        - Output is paginated (40 lines per page) and formatted in monospace font for clarity.
    """

    all_lines = []
    for column_name in column_names:
        description = column_descriptions.get(column_name, column_name)
        all_lines.append(f"{description}:")
        values = [str(val) for val in df[column_name] if not pd.isna(val)]
        for val in values:
            wrapped = textwrap.wrap(val, width=max_line_length) or ['']
            if wrapped:
                all_lines.append(f"- {wrapped[0]}")
                for cont_line in wrapped[1:]:
                    all_lines.append(f"  {cont_line}")
            else:
                all_lines.append("-")
        all_lines.append("")  # Add a blank line after each column for separation

    # Split all_lines into pages of 40 lines each
    lines_per_page = 40
    pages = [all_lines[i:i + lines_per_page] for i in range(0, len(all_lines), lines_per_page)]

    with PdfPages(output_file) as pdf:
        for page in pages:
            fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 size in inches
            ax.axis('off')
            text = "\n".join(page)
            ax.text(0, 1, text, va='top', ha='left', fontsize=10, family='monospace')
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)