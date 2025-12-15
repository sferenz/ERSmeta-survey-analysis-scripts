"""
print_figures.py

This module provides functions for generating publication-ready figures (boxplots, pie charts, bar charts)
from survey and metadata analysis using Matplotlib and pandas. It is designed for use in the ERSmeta
evaluation pipeline and supports Likert-scale data, grouped visualizations, and LaTeX-compatible output.

Main Features:
- Horizontal boxplots for Likert-scale survey responses, with groupings, background regions, and annotated statistics.
- Pie charts for categorical distributions, with descriptive labels and value counts.
- Bar charts for "yes" counts across multiple columns.
- Utilities for combining multiple PDF figures into a single report.
- All figures are saved as both PDF and PNG files for easy inclusion in LaTeX documents.

Functions:
- _plot_boxplots_with_background: Internal helper for boxplot rendering with background and group headings.
- generate_pdf_with_boxplots: Create a multi-row boxplot PDF for multiple columns.
- generate_pdf_with_boxplot_for_series: Create a single boxplot PDF for a data series.
- generate_pdf_sus: Visualize System Usability Scale (SUS) scores as a boxplot with background categories.
- plot_column_pie_chart_pdf: Generate a pie chart for a single column's value distribution.
- plot_pie_chart_from_value_counts: Generate a pie chart from a value_counts Series.
- plot_yes_counts_bar_chart_pdf: Generate a bar chart for "yes" counts in specified columns.
- combine_pdfs_in_folder: Merge all PDF files in a folder into a single PDF.

Assumptions and Notes:
- Likert-scale mapping is defined in LIKERT_MAPPING and used throughout for survey data.
- All output figures are intended for academic publication and LaTeX integration.
- Requires: pandas, numpy, matplotlib, PyPDF2

"""
import pandas as pd
import numpy as np
import textwrap
import os

import matplotlib.pyplot as plt
import matplotlib.lines as mlines

from PyPDF2 import PdfMerger
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Patch

# Mapping for Likert-scale responses to numeric values
LIKERT_MAPPING = {
    "Strongly Disagree": 1,
    "Disagree": 2,
    "Neutral": 3,
    "Agree": 4,
    "Strongly Agree": 5
}
LIKERT_LABELS = [
    "Strongly\nDisagree",
    "Disagree",
    "Neutral",
    "Agree",
    "Strongly\nAgree"
]
LIKERT_TICKS = list(LIKERT_MAPPING.values())

def _plot_boxplots_with_background(
    ax,
    boxplot_data,
    ytick_labels,
    means,
    variances,
    overall_title=None,
    couting_factor=None,
    columns=None,
    show_ylabels=True,
    group_names=None,
    group_lengths=None,
    fig=None
):
    """
    Internal helper to plot horizontal boxplots with background color regions per row.
    Supports group headings, mean/variance annotation, and custom background for positive/negative items.

    Args:
        ax (matplotlib.axes.Axes): The axes to plot on.
        boxplot_data (list of pd.Series): Data for each boxplot.
        ytick_labels (list of str): Y-tick labels for each boxplot.
        means (list of float): Mean values for annotation.
        variances (list of float): Variance values for annotation.
        overall_title (str, optional): Title for the plot.
        couting_factor (dict, optional): Dict mapping column names to bool for background direction.
        columns (list, optional): List of column names (for background coloring).
        show_ylabels (bool): Whether to show y-tick labels.
        group_names (list, optional): Names of groups for grouped boxplots.
        group_lengths (list, optional): Lengths of each group.
        fig (matplotlib.figure.Figure, optional): Figure object for setting suptitle.
    """

    num_plots = len(boxplot_data)
    if columns is None:
        columns = [str(i) for i in range(num_plots)]
    if couting_factor is None:
        couting_factor = {}

    # Draw background color regions for each row based on couting_factor
    for i, col in enumerate(columns):
        y_bottom = i + 0.5
        y_top = i + 1.5
        is_normal = couting_factor.get(col, True)
        if is_normal:
            # Not acceptable (1-3)
            ax.axvspan(1, 3, ymin=(y_bottom-0.5)/num_plots, ymax=(y_top-0.5)/num_plots, color='#ffcccc', alpha=0.4)
            # Acceptable (3-5)
            ax.axvspan(3, 5, ymin=(y_bottom-0.5)/num_plots, ymax=(y_top-0.5)/num_plots, color='#d9ead3', alpha=0.4)
        else:
            # Acceptable (1-3)
            ax.axvspan(1, 3, ymin=(y_bottom-0.5)/num_plots, ymax=(y_top-0.5)/num_plots, color='#d9ead3', alpha=0.4)
            # Not acceptable (3-5)
            ax.axvspan(3, 5, ymin=(y_bottom-0.5)/num_plots, ymax=(y_top-0.5)/num_plots, color='#ffcccc', alpha=0.4)

    # Create horizontal boxplots
    bplots = ax.boxplot(
        boxplot_data,
        vert=False,
        patch_artist=True,
        labels=ytick_labels if show_ylabels else [''] * len(ytick_labels),
        showmeans=True,
        meanline=True,
        medianprops={'linewidth': 4, 'color': 'red', 'linestyle': 'solid'},
        meanprops={'linewidth': 3, 'color': 'orange', 'linestyle': 'solid'},
    )

    if show_ylabels:
        ax.set_yticklabels(ytick_labels, fontsize=10)
    else:
        ax.set_yticklabels([])

    ax.set_xticks(LIKERT_TICKS)
    ax.set_xticklabels(LIKERT_LABELS, rotation=0)

    # Annotate mean and variance for each boxplot
    for i, (mean, var) in enumerate(zip(means, variances), start=1):
        if not np.isnan(mean):
            ax.text(LIKERT_TICKS[-1] + 0.3, i, f"Mean: {mean:.2f}\nVar: {var:.2f}", va='center', fontsize=10)

    # Draw dotted line between groups and add group headings
    if group_names and group_lengths and len(group_lengths) > 1:
        y_offset = 0
        for idx, (gname, glen) in enumerate(zip(group_names, group_lengths)):
            # Add rotated group heading
            #x_pos = -0.52  # Position to the left of y-axis
            x_pos = -1.27  # Position to the left of y-axis
            #y_center = y_offset + (glen-1) / 2.0 + 2.5
            y_center = y_offset + (glen)
            ax.text(
                x_pos, y_center, gname,
                va='center', ha='right',
                fontsize=12, fontweight='bold',
                rotation=90, rotation_mode='anchor',
                transform=ax.get_yaxis_transform()
            )
            y_offset += glen
            # Draw dotted line after each group except the last
            if idx < len(group_lengths) - 1:
                ax.axhline(y=y_offset + 0.5, color='black', linestyle='dotted', linewidth=1)

    # Create custom legend handles for mean and median
    median_line = mlines.Line2D([], [], color='red', linewidth=4, linestyle='solid', label='Median')
    mean_line = mlines.Line2D([], [], color='orange', linewidth=3, linestyle='solid', label='Mean')
    handles = [mean_line, median_line]

    # Add the legend below the x-axis
    ax.legend(
        handles=handles,
        loc='upper center',
        bbox_to_anchor=(0.5, -0.05),  # Place legend below the axes
        ncol=len(handles),
        frameon=True
    )
    if overall_title and fig:
        # Adjust width as needed (e.g., 60 characters)
        wrapped_title = "\n".join(textwrap.wrap(overall_title, width=70))
        fig.suptitle(wrapped_title, fontsize=16, fontweight='bold', y=0.98, x=0.1)


    #plt.subplots_adjust(left=0.25, right=0.55, top=0.92, bottom=0.10)

    #plt.tight_layout(rect=[0.15, 0, 0.95, 1])

def generate_pdf_with_boxplots(
    df,
    columns,
    output_pdf,
    column_description_dict=None,
    overall_title=None,
    couting_factor=None,
    groups=None
):
    """
    Generates a PDF with one row per column: description (or name), mean, variance, and a horizontal box plot.
    Converts Likert-scale enums to numeric values for statistics, but displays original labels on the x-axis.
    Supports grouping and background coloring for positive/negative items.

    Args:
        df (pd.DataFrame): DataFrame with data.
        columns (list of str): Columns to analyze.
        output_pdf (str): Path to output PDF file.
        column_description_dict (dict, optional): Dictionary mapping column names to descriptions.
        overall_title (str, optional): Overall title to display as a single title page.
        couting_factor (dict, optional): Dict mapping column names to bool for background direction.
        groups (dict, optional): Grouping of columns for visual separation.
    """
    # Invert the order of columns at the beginning
    columns = list(columns)[::-1]

    boxplot_data = []
    ytick_labels = []
    means = []
    variances = []

    max_desc_width = 60
    max_desc_lines = 5

    # Deal with group information
    if groups is not None:
        # Build ensure the group order matches the column order
        column_to_group = {}
        for group_name, cols in groups.items():
            for col in cols:
                column_to_group[col] = group_name
        group_order = []
        seen = set()
        for col in columns:
            group = column_to_group.get(col)
            if group and group not in seen:
                group_order.append(group)
                seen.add(group)
        group_names = group_order
        group_columns = [groups[name] for name in group_names]
        group_lengths = [len(cols) for cols in group_columns]
    else:
        group_names = None
        group_lengths = None

    # Calculate total number of valid answers (non-NaN) across all columns
    n_answers = int(df[columns].notna().any(axis=1).sum())
    if overall_title:
        overall_title = f"{overall_title} (n={n_answers})"

    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            data = df[col].dropna()
        else:
            data = df[col].map(LIKERT_MAPPING).dropna()
        if len(data) == 0:
            data = pd.Series([np.nan])
        boxplot_data.append(data)
        desc = column_description_dict.get(col, col) if column_description_dict else col
        wrapped = textwrap.wrap(desc, width=max_desc_width)
        if len(wrapped) > max_desc_lines:
            wrapped = wrapped[:max_desc_lines]
            wrapped[-1] += '...'
        ytick_labels.append('\n'.join(wrapped))
        means.append(data.mean())
        variances.append(data.var())

    num_plots = len(boxplot_data)
    fig_height = max(6, 0.7 * num_plots)
    fig, ax = plt.subplots(figsize=(4, fig_height))
    #fig.subplots_adjust(left=0.32) 

    _plot_boxplots_with_background(
        ax,
        boxplot_data,
        ytick_labels,
        means,
        variances,
        overall_title=overall_title,
        couting_factor=couting_factor,
        columns=columns,
        show_ylabels=True,
        group_names=group_names,
        group_lengths=group_lengths,
        fig=fig
    )

    with PdfPages(output_pdf) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
        fig.savefig(output_pdf.replace('.pdf', '.png'), bbox_inches='tight')
    plt.close(fig)

def generate_pdf_with_boxplot_for_series(
    data_series,
    output_pdf,
    description="",
    overall_title=None,
    couting_factor=None
):
    """
    Generates a PDF with a single boxplot for a data series, with background color regions.
    Useful for visualizing aggregated or composite scores.

    Args:
        data_series (pd.Series): The data to plot.
        output_pdf (str): Path to output PDF file.
        description (str): Description for the y-tick label.
        overall_title (str, optional): Overall title to display as the figure heading.
        couting_factor (dict, optional): Dict mapping the series name to bool for background direction.
    """
    n_answers = int(data_series.notna().sum())
    if overall_title:
        overall_title = f"{overall_title} (n={n_answers})"

    data = data_series
    if len(data) == 0:
        data = pd.Series([np.nan])
    boxplot_data = [data]
    ytick_labels = [description]
    if len(description) > 2:
        show_ylabels=True
    else:
        show_ylabels=False
    means = [data.mean()]
    variances = [data.var()]
    columns = [data_series.name if data_series.name else "Value"]

    fig, ax = plt.subplots(figsize=(10, 3))

    _plot_boxplots_with_background(
        ax,
        boxplot_data,
        ytick_labels,
        means,
        variances,
        overall_title=overall_title,
        couting_factor=couting_factor,
        columns=columns,
        show_ylabels=show_ylabels,
        fig=fig
    )

    with PdfPages(output_pdf) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
        fig.savefig(output_pdf.replace('.pdf', '.png'), bbox_inches='tight')
    plt.close(fig)

def generate_pdf_sus(sus_input, output_pdf, title=None):
    """
    Visualizes the SUS (System Usability Scale) scores as a boxplot with background categories:
    - Acceptable (70-100, green)
    - Marginal (50-70, yellow)
    - Not acceptable (0-50, red)
    Handles both single series and dicts of series for grouped SUS visualizations.

    Args:
        sus_input (pd.Series or dict): Series containing SUS scores, or dict of {label: pd.Series}.
        output_pdf (str): Path to the output PDF file.
        title (str, optional): Title for the plot.
    """
    # Handle single series or dict of series      
    if isinstance(sus_input, dict):
        sus_dict = sus_input
    else:
        sus_dict = {title: sus_input}

    # Prepare data
    boxplot_data = []
    ytick_labels = []
    means = []
    variances = []
    n_answers_max = 0

    for label, series in sus_dict.items():
        sus_clean = series.dropna()
        n_answers = int(sus_clean.shape[0])
        if n_answers > n_answers_max:
            n_answers_max = n_answers
        boxplot_data.append(sus_clean)
        ytick_labels.append(f"{label} (n={n_answers})")
        means.append(sus_clean.mean())
        variances.append(sus_clean.var())

    num_plots = len(boxplot_data)
    fig_height = max(4, 0.7 * num_plots)
    fig, ax = plt.subplots(figsize=(10, fig_height))

    # Draw background category regions
    for i in range(num_plots):
        y_bottom = i + 0.5
        y_top = i + 1.5
        ax.axvspan(0, 50, ymin=(y_bottom-0.5)/num_plots, ymax=(y_top-0.5)/num_plots, color='#ffcccc', alpha=0.5)
        ax.axvspan(50, 70, ymin=(y_bottom-0.5)/num_plots, ymax=(y_top-0.5)/num_plots, color='#fff2cc', alpha=0.5)
        ax.axvspan(70, 100, ymin=(y_bottom-0.5)/num_plots, ymax=(y_top-0.5)/num_plots, color='#d9ead3', alpha=0.5)

    # Boxplot
    bplot = ax.boxplot(
        boxplot_data,
        vert=False,
        patch_artist=True,
        showmeans=True,
        meanline=True,
        medianprops={'linewidth': 4, 'color': 'red', 'linestyle': 'solid'},
        meanprops={'linewidth': 3, 'color': 'orange', 'linestyle': 'solid'},
        labels=ytick_labels
    )

    ax.set_yticklabels(ytick_labels, fontsize=12)
    ax.set_xlim(0, 100)
    for label in ax.get_xticklabels():
        label.set_fontsize(12)
    ax.set_xlabel("SUS Score", fontsize=12)
    if title:
        if isinstance(sus_input, dict):
            ax.set_title(f"{title} (total n={n_answers_max})", fontsize=14, fontweight='bold')
        else:
            ax.set_title(title, fontsize=14, fontweight='bold')

    # Annotate mean and variance for each boxplot
    for i, (mean, var) in enumerate(zip(means, variances), start=1):
        if not np.isnan(mean):
            #ax.text(102, i, f"Mean: {mean:.2f}\nVar: {var:.2f}", va='center', fontsize=9)
            ax.text(102, i, f"Mean: {mean:.2f}", va='center', fontsize=12)

    # Custom legend for categories
    legend_elements = [
        Patch(facecolor='#d9ead3', edgecolor='gray', alpha=0.5, label='Acceptable (70-100)'),
        Patch(facecolor='#fff2cc', edgecolor='gray', alpha=0.5, label='Marginal (50-70)'),
        Patch(facecolor='#ffcccc', edgecolor='gray', alpha=0.5, label='Not acceptable (0-50)')
    ]

    # Create custom legend handles for mean and median
    median_line = mlines.Line2D([], [], color='red', linewidth=4, linestyle='solid', label='Median')
    mean_line = mlines.Line2D([], [], color='orange', linewidth=3, linestyle='solid', label='Mean')
    handles = [mean_line, median_line] + legend_elements

    # Add the legend below the x-axis
    ax.legend(
        handles=handles,
        loc='upper right',
        frameon=True,
        fontsize=12
    )

    plt.tight_layout()
    with PdfPages(output_pdf) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
        fig.savefig(output_pdf.replace('.pdf', '.png'), bbox_inches='tight')
    plt.close(fig)

def plot_column_pie_chart_pdf(df, column, output_pdf, column_description_dict):
    """
    Prepares value counts and calls plot_pie_chart_from_value_counts to generate a pie chart PDF.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        column (str): The column name to analyze.
        output_pdf (str): The path to save the pie chart PDF.
        column_description_dict (dict): Dictionary mapping column names to descriptions.
    """
     # Replace empty strings and NaN with 'No information provided'
    col_data = df[column].replace('', pd.NA)
    col_data = col_data.fillna('No information provided')
    value_counts = col_data.value_counts(dropna=False)
    n_answers = len(col_data)
    title = f"Distribution of {column_description_dict.get(column, column)} (n={n_answers})"
    plot_pie_chart_from_value_counts(value_counts, output_pdf, column_description_dict, title)

def plot_pie_chart_from_value_counts(value_counts, output_pdf, column_description_dict, title):
    """
    Plots a pie chart from a value_counts Series and saves it as a PDF.
    Each slice is annotated with its description and value count.

    Args:
        value_counts (pd.Series): Value counts for categories.
        output_pdf (str): Path to save the pie chart PDF.
        column_description_dict (dict): Dictionary mapping category names to descriptions.
        title (str): Title for the chart.
    """
     # Prepare descriptions for each category
    categories = value_counts.index.astype(str)
    descriptions = []
    max_box_width = 30  # characters per line in the box
    max_box_lines = 4   # max lines per box

    for cat in categories:
        desc = column_description_dict.get(cat, cat)
        # Line-break the description
        wrapped = textwrap.wrap(desc, width=max_box_width)
        # Limit to max_box_lines, add ellipsis if too long
        if len(wrapped) > max_box_lines:
            wrapped = wrapped[:max_box_lines]
            wrapped[-1] += '...'
        descriptions.append('\n'.join(wrapped))

    def autopct_format(pct, allvals):
        absolute = int(round(pct/100.*sum(allvals)))
        return f"{pct:.1f}%\n({absolute})"

    # Set up a fixed-size figure for consistency
    fig, ax = plt.subplots(figsize=(8, 8))

    # Pie chart
    wedges, texts, autotexts = ax.pie(
        value_counts.values,
        labels=None,  # No labels on the pie itself
        autopct=lambda pct: autopct_format(pct, value_counts.values),
        startangle=90,
        counterclock=False,
        textprops={'fontsize': 10},
        radius=1.0
    )
    ax.set_title(title)
    ax.axis('equal')  # Equal aspect ratio for a perfect circle

     # Draw description boxes next to corresponding pie slices
    # Calculate the angle for each wedge to position the box
    total = sum(value_counts.values)
    angles = []
    current_angle = 90  # startangle
    for count in value_counts.values:
        angle = 360 * count / total
        angles.append((current_angle - angle / 2) % 360)
        current_angle -= angle

    # Place description boxes
    for i, (angle, desc, wedge) in enumerate(zip(angles, descriptions, wedges)):
        # Convert angle to radians
        theta = np.deg2rad(angle)
        # Position: just outside the pie (r=1.2)
        r = 1.2
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        # Draw a box with background color matching the wedge
        bbox_props = dict(boxstyle="round,pad=0.4", fc=wedge.get_facecolor(), ec="gray", alpha=0.25)
        ax.text(
            x, y, desc,
            ha='center', va='center', fontsize=10, family='monospace',
            bbox=bbox_props, wrap=True
        )

    plt.tight_layout()
    with PdfPages(output_pdf) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
        fig.savefig(output_pdf.replace('.pdf', '.png'), bbox_inches='tight')
    plt.close(fig)

def plot_yes_counts_bar_chart_pdf(df, columns, column_description_dict, output_pdf, chart_title):
    """
    Counts 'yes' values in specified columns and plots them as a bar chart in a PDF.
    Uses column descriptions for bar labels.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        columns (list of str): List of column names to analyze.
        column_description_dict (dict): Dictionary mapping column names to descriptions.
        output_pdf (str): Path to save the bar chart PDF (e.g., 'yes_counts.pdf').
        chart_title (str): Title for the bar chart.
    """
    # Count 'yes' in each column
    yes_counts = []
    bar_labels = []

    n_answers = int(df[columns].notna().any(axis=1).sum())
    chart_title = f"{chart_title} (n={n_answers})"

    for col in columns:
        count = (df[col].str.lower() == 'yes').sum()
        yes_counts.append(count)
        bar_labels.append(column_description_dict.get(col, col))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(bar_labels, yes_counts, color='skyblue')
    ax.set_ylabel("Number")
    ax.set_title(f"{chart_title}")

    # Rotate and align x-tick labels, and ensure they fit
    plt.xticks(rotation=45, ha='right', fontsize=10, wrap=True)
    plt.tight_layout(rect=[0, 0, 1, 0.95])  # Leave space for title
    plt.tight_layout()
    with PdfPages(output_pdf) as pdf:
        pdf.savefig(fig, bbox_inches='tight')
        fig.savefig(output_pdf.replace('.pdf', '.png'), bbox_inches='tight')
    plt.close(fig)

def combine_pdfs_in_folder(folder_path, output_pdf):
    """
    Combines all PDF files in the specified folder into a single PDF.

    Args:
        folder_path (str): Path to the folder containing PDF files.
        output_pdf (str): Path to the output combined PDF file.
    """
    merger = PdfMerger()
    # List all PDF files in the folder, sorted alphabetically
    pdf_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')])
    for pdf_file in pdf_files:
        merger.append(os.path.join(folder_path, pdf_file))
    merger.write(output_pdf)
    merger.close()