"""
create_survey_statistics.py

This module provides functions to generate summary statistics and visualizations for survey data,
specifically for demographic information, prior experience, and dropout reasons. It produces
publication-ready figures (pie charts, bar charts) and exports selected columns to text and PDF files.

Functions:
- generate_demographics_diagrams: Create demographic figures and exports for survey participants.
- generate_prior_experience_diagrams: Visualize participants' prior experience with metadata and ERS.
- generate_dropout_reasons_diagrams: Summarize and visualize survey dropout and completion reasons.

All functions expect a pandas DataFrame with survey responses as input.
"""
import pandas as pd

from print_figures import plot_column_pie_chart_pdf, plot_yes_counts_bar_chart_pdf, plot_pie_chart_from_value_counts
from write_column import write_column_to_txt, write_column_to_pdf

def generate_demographics_diagrams(
    df: pd.DataFrame,
    filename_prefix: str = "",
    title_suffix: str = ""
) -> None:
    """
    Generates all demographic diagrams (pie charts, bar charts, txt/pdf exports) for the given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the survey data.
        filename_prefix (str, optional): Prefix for all output files. Default is "".
        title_suffix (str, optional): Suffix for all diagram titles. Default is "".

    Output:
        - Pie charts for position, experience, and domain.
        - Bar chart for affiliation.
        - Text and PDF exports for "other" positions and keywords.
        - All files are saved with the specified filename prefix.
    """
    columns_description={
        "G00Q02":"Position in the Institution",
        "G00Q03":"Experience",
        "G00Q04":"Domain"
    }
    files_names={
        "G00Q02":"Q02_Positions",
        "G00Q03":"Q03_Experience",
        "G00Q04":"Q04_Domain"
    }
    pie_chart_columns= columns_description.keys()
    bar_chart_columns_dict={
        "G02Q02": ["G02Q02[SQ001]","G02Q02[SQ005]","G02Q02[SQ002]","G02Q02[SQ003]","G02Q02[SQ004]"]
    }
    bar_chart_columns_description={
        'G02Q02[SQ001]':'University',
        'G02Q02[SQ005]':'University of Applied Sciences',
        'G02Q02[SQ002]':'Non-University Research Institution',
        'G02Q02[SQ003]':'Other Scientific Institution',
        'G02Q02[SQ004]':'Industry'
    }
    bar_chart_files_names={"G02Q02":"Q01_Affiliation"}
    bar_chart_titles={"G02Q02":"Affiliation of the Participants"}

    txt_pdf_files_names={
        "G00Q02[other]":"Q02_Other_Positions",
        "G00Q05":"Q05_keywords"
    }
    txt_pdf_columns=txt_pdf_files_names.keys()
    txt_pdf_columns_descriptions={
        "G00Q02[other]":"Other_Positions",
        "G00Q05":"Keywords"
    }
    # Add title_suffix to each description in columns_description
    columns_description = {
        k: v + title_suffix for k, v in columns_description.items()
    }
    txt_pdf_columns_descriptions = {
        k: v + title_suffix for k, v in txt_pdf_columns_descriptions.items()
    }

    # Pie charts
    for col in pie_chart_columns:
        name = files_names.get(col, col)
        plot_column_pie_chart_pdf(
            df,
            col,
            f"{filename_prefix}Demographics_{name}_pie_chart.pdf",
            columns_description
        )

    # Bar charts
    for group, cols in bar_chart_columns_dict.items():
        name = bar_chart_files_names.get(group, group)
        chart_title = bar_chart_titles.get(group, group) + title_suffix
        plot_yes_counts_bar_chart_pdf(
            df,
            cols,
            bar_chart_columns_description,
            f"{filename_prefix}Demographics_{name}_bar_chart.pdf",
            chart_title
        )

    # TXT/PDF exports
    for col in txt_pdf_columns:
        name = txt_pdf_files_names.get(col, col)
        col_list = [col]  # Ensure col is a list for consistency
        write_column_to_txt(
            df,
            col_list,
            f"{filename_prefix}Demographics_{name}_values.txt",
            txt_pdf_columns_descriptions
        )
        write_column_to_pdf(
            df,
            col_list,
            f"{filename_prefix}Demographics_{name}_values.pdf",
            txt_pdf_columns_descriptions
        )


def generate_prior_experience_diagrams(
    df: pd.DataFrame,
    filename_prefix: str = "",
    title_suffix: str = ""
) -> None:
    """
    Generates all prior experience diagrams (pie charts, bar charts) for the given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the survey data.
        filename_prefix (str, optional): Prefix for all output files. Default is "".
        title_suffix (str, optional): Suffix for all diagram titles. Default is "".

    Output:
        - Pie charts for metadata schema familiarity, ERS development involvement, chosen ERS, and metadata creation.
        - Bar chart for ERS experience.
        - All files are saved with the specified filename prefix.
    """
    pie_chart_columns_description={
        "G02Q06":"Familarity with Metadata Schemas",
        "G02Q08":"Involvement in ERS Developement",
        "G00Q09": "Choosen ERS for Evaluation",
        "G03Q10": "Finalized Creation of Metadata"
    }
    pie_chart_columns = pie_chart_columns_description.keys()
    pie_chart_files_names={
        "G02Q06":"Q06_metadata_schema_experience",
        "G02Q08":"Q08_ERS_development_involvement",
        "G00Q09":"Q09_Choosen_ERS",
        "G03Q10": "Q10_finalized_creation"
    }
    bar_chart_columns_dict={
        "G02Q07": ["G02Q07[SQ002]","G02Q07[SQ003]","G02Q07[SQ004]","G02Q07[SQ005]"]
    }
    bar_chart_columns_description={
        'G02Q07[SQ002]':'I have been involved in the development of one or more energy research software.',
        'G02Q07[SQ003]':'I have used an energy research software for my research.',
        'G02Q07[SQ004]':'I know what an energy research software is but have not used one yet.',
        'G02Q07[SQ005]':'I am not familiar with energy research software.'
    }
    bar_chart_files_names={"G02Q07":"Q07_ERS_experience"}
    bar_chart_titles={"G02Q07": "Experience with ERS"}

    # Add title_suffix to each description in pie_chart_columns_description
    pie_chart_columns_description = {
        k: v + title_suffix for k, v in pie_chart_columns_description.items()
    }
    # Pie charts
    for col in pie_chart_columns:
        name = pie_chart_files_names.get(col, col)
        plot_column_pie_chart_pdf(
            df,
            col,
            f"{filename_prefix}Experience_{name}_pie_chart.pdf",
            pie_chart_columns_description
        )

    # Bar charts
    for group, cols in bar_chart_columns_dict.items():
        name = bar_chart_files_names.get(group, group)
        chart_title = bar_chart_titles.get(group, group) + title_suffix
        plot_yes_counts_bar_chart_pdf(
            df,
            cols,
            bar_chart_columns_description,
            f"{filename_prefix}Experience_{name}_bar_chart.pdf",
            chart_title
        )

def generate_dropout_reasons_diagrams(
    df: pd.DataFrame,
    filename_prefix: str = "",
    title_suffix: str = ""
) -> None:
    """
    Generates a pie chart summarizing survey completion and dropout reasons.

    Args:
        df (pd.DataFrame): The DataFrame containing the survey data.
        filename_prefix (str, optional): Prefix for the output file. Default is "".
        title_suffix (str, optional): Suffix for the chart title. Default is "".

    Output:
        - Pie chart showing the distribution of participant completion and dropout reasons.
        - The file is saved as "{filename_prefix}participant_types_pie_chart.pdf".
        - Prints a warning if the sum of categorized states does not match the number of participants.
    """
    states = {
        "Not started": df['lastpage'].isna().sum() + (df['lastpage'] == '').sum() + (df['lastpage'] == -1).sum(),
        "Stop during demographics": (df['lastpage'] == 1).sum()+ (df['lastpage'] == 0).sum(),
        "Stop during evaluation part": df['lastpage'].isin([i for i in range(4, 12)]).sum() + (
                (df['lastpage'] == 3) &
                (df['G03Q10'] == "Yes.")
            ).sum(),
        "Closed repository": (
                (df['lastpage'] == 2) &
                (df['G00Q09'] == "The chosen software is in a closed GitHub or GitLab repository.")
            ).sum(),
        "Software is not available": (
                (df['lastpage'] == 2) &
                (df['G00Q09'] == "The chosen software is not available on GitHub or GitLab.")
            ).sum(),
        "No feedback after starting SMECS": (
                (df['lastpage'] == 2) &
                (df['G00Q09'] == "The chosen software is openly available as a GitHub or GitLab repository.")
            ).sum(),
        "Technical issues": (
                (df['lastpage'] == 3) &
                (df['G03Q10'] == "No, there were technical issues.")
            ).sum(),
        "Not enough time": (
                (df['lastpage'] == 3) &
                (df['G03Q10'] == "No, I do not have enough time for that.")
            ).sum(),
        "Finalized evaluation":  (df['lastpage'] == 12).sum()
        }

    states_sum = sum(v for v in states.values())
    overall_participants = len(df)
    if (states_sum != overall_participants):
        print(f"Warning: Sum of state counts {states_sum} does not match overall participants{overall_participants}.")

     # Convert states dict to pandas Series
    states_series = pd.Series(states)

    # Optionally, provide a description dict for the pie chart
    description_dict = {k: k for k in states_series.index}

    # Set a title for the chart
    chart_title = f"Survey Completion and Dropout Reasons{title_suffix}"

    # Plot using the inner function
    plot_pie_chart_from_value_counts(
        states_series,
        output_pdf=f"{filename_prefix}participant_types_pie_chart.pdf",
        column_description_dict=description_dict,
        title=chart_title
    )