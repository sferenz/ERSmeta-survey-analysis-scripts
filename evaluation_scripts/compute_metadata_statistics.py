"""
compute_metadata_statistics.py

This module provides utility functions for analyzing and summarizing metadata sets
according to a given schema. It includes functions to extract subsets of elements,
determine element priority, and count the presence or multiplicity of elements
across multiple metadata records.

Functions:
- get_element_subset: Extract a sublist of element names between two specified elements.
- get_priority: Determine the priority (required, recommended, optional) of a property in a schema.
- count_elements_per_metadata: Count how many elements from a list are present in each metadata set.
- count_items_per_element: Count the number of items for specific elements in each metadata set.
"""
import pandas as pd

def get_element_subset(element_names: list, start_element: str, end_element: str) -> list:
    """
    Returns a sublist of element_names from start_element to end_element (inclusive).

    Args:
        element_names (list of str): The full list of element names (ordered).
        start_element (str): The name of the first element in the desired subset.
        end_element (str): The name of the last element in the desired subset.

    Returns:
        list of str: Sublist of element names from start_element to end_element, inclusive.

    Raises:
        ValueError: If start_element or end_element is not found in element_names.
    """
    start_idx = element_names.index(start_element)
    end_idx = element_names.index(end_element)
    return element_names[start_idx:end_idx + 1]

def get_priority(prop: str, metadata_schema: dict) -> str:
    """
    Determines the priority of a property in the metadata schema.

    Args:
        prop (str): The property name to check.
        metadata_schema (dict): The metadata schema dictionary, which should contain
            'required' and 'recommended' lists.

    Returns:
        str: One of 'required', 'recommended', or 'optional' depending on the property's status.
    """
    if prop in metadata_schema['required']:
        return 'required'
    elif prop in metadata_schema['recommended']:
        return 'recommended'
    else:
        return 'optional'

def count_elements_per_metadata(
    element_list: list,
    metadata_list: list,
    name: str
) -> pd.Series:
    """
    For each metadata set, count how many elements from element_list are present.

    Args:
        element_list (list of str): List of element names to check for presence.
        metadata_list (list of dict): List of metadata dictionaries (one per metadata set).
        name (str): Name for the resulting Series (typically the group or category name).

    Returns:
        pd.Series: Series with the count of present elements for each metadata set,
                   indexed by metadata set order, and named as specified by 'name'.

    Example:
        >>> count_elements_per_metadata(['a', 'b'], [{'a': 1}, {'b': 2, 'c': 3}], 'Test')
        0    1
        1    1
        Name: Test, dtype: int64
    """
    counts = [
        sum(elem in metadata for elem in element_list)
        for metadata in metadata_list
    ]
    return pd.Series(counts, name=name)

def count_items_per_element(
    metadata_list: list,
    elements_with_items: list
) -> pd.DataFrame:
    """
    Creates a DataFrame where each row corresponds to a metadata set,
    each column to an element in elements_with_items, and each cell contains
    the number of items for that element in the respective metadata set.

    Args:
        metadata_list (list of dict): List of metadata dictionaries (one per metadata set).
        elements_with_items (list of str): List of element names to count items for.

    Returns:
        pd.DataFrame: DataFrame of shape (len(metadata_list), len(elements_with_items)),
                      where each cell is the count of items (length of list) for that element,
                      or 0 if the element is not present or not a list.

    Example:
        >>> count_items_per_element(
        ...     [{'a': [1,2], 'b': [3]}, {'a': [], 'b': [4,5,6]}],
        ...     ['a', 'b']
        ... )
           a  b
        0  2  1
        1  0  3
    """
    rows = []
    for metadata in metadata_list:
        row = {}
        for element in elements_with_items:
            value = metadata.get(element, [])
            # Count items if value is a list, else 0
            if isinstance(value, list):
                row[element] = len(value)
            else:
                row[element] = 0
        rows.append(row)
    return pd.DataFrame(rows, columns=elements_with_items)