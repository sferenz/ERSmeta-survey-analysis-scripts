"""
compute_column_statistics.py

Provides functions for calculating statistical measures (mean, variance) and System Usability Scale (SUS) scores
from survey data in pandas DataFrames. Handles Likert-scale mapping and supports both positively and negatively
worded items.

Functions:
- calculate_mean_variance: Compute mean and variance for specified columns.
- calculate_sus: Compute SUS scores for each row based on column polarity.
- calculate_mean_values: Compute row-wise mean for Likert-scale columns with polarity handling.
"""

import pandas as pd
from typing import List, Dict, Tuple

def calculate_mean_variance(
    df: pd.DataFrame, 
    columns: list[str]
) -> dict[str, tuple[float, float]]:
    """
    Calculates the mean and variance for the specified columns in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        columns (list of str): List of column names to analyze.

    Returns:
        dict: A dictionary where keys are column names and values are (mean, variance) tuples.
    """
    stats = {}
    for col in columns:
        mean = df[col].mean()
        variance = df[col].var()
        stats[col] = (mean, variance)
    return stats


def calculate_sus(
    df: pd.DataFrame,
    counting: Dict[str, bool]
) -> pd.Series:
    """
    Calculates the System Usability Scale (SUS) score for each row in the DataFrame.

    Args:
        df (pd.DataFrame): DataFrame containing survey responses, with columns corresponding to SUS items.
        counting (dict): Dictionary mapping column names to booleans.
            - True: Column is positively worded (higher Likert value is better).
            - False: Column is negatively worded (higher Likert value is worse).

    Returns:
        pd.Series: SUS scores for each row, scaled from 0 to 100.

    Notes:
        - Likert responses are mapped as follows:
            "Strongly Disagree"=1, "Disagree"=2, "Neutral"=3, "Agree"=4, "Strongly Agree"=5
        - Missing values are treated as zeros in the calculation.
        - Raises ValueError if a specified column is not found in the DataFrame.
    """
    likert_mapping = {
        "Strongly Disagree": 1,
        "Disagree": 2,
        "Neutral": 3,
        "Agree": 4,
        "Strongly Agree": 5
    }
    data = pd.Series(0, index=df.index, dtype=float)

    for col, couting_positive in counting.items():
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame.")
        mapped = df[col].map(likert_mapping)
        if couting_positive:
            data += (mapped - 1).fillna(0)
        else:
            data +=  (5 - mapped).fillna(0)

    data = data * 2.5
    
    return data


def calculate_mean_values(
    df: pd.DataFrame,
    counting: Dict[str, bool]
) -> pd.Series:
    """
    Calculates the mean value for each row in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        counting (dict): Dictionary mapping column names to booleans.
                         True for positively worded items, False for negatively worded.

    Returns:
        pd.Series: SUS scores for each row.
    """
    likert_mapping = {
        "Strongly Disagree": 1,
        "Disagree": 2,
        "Neutral": 3,
        "Agree": 4,
        "Strongly Agree": 5
    }
    data = pd.Series(0, index=df.index, dtype=float)


    for col, couting_positive in counting.items():
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in DataFrame.")
        mapped = df[col].map(likert_mapping)
        if couting_positive:
            data += mapped.fillna(0)
        else:
            data +=  (6 - mapped).fillna(0)

    data = data / len(counting)
    
    return data
