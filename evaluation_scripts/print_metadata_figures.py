"""
print_metadata_figures.py

This module provides functions for visualizing metadata element statistics for metadata created based on ERSmeta.
It generates publication-ready bar charts and boxplots for metadata element usage, priority, and cardinality.
The figures are designed for inclusion in academic reports and LaTeX documents.

Main Features:
- Bar chart (histogram) of element occurrence across metadata sets, colored by priority and position.
- Horizontal boxplots for element type counts, with optional annotation of mean/variance and overlay of maximal values.
- Color utilities for visually distinguishing element priorities and positions.

Functions:
- adjust_color_intensity: Lightens or darkens a base color based on element position.
- get_bar_color: Assigns a color to a bar based on element priority and position.
- save_element_histogram: Creates and saves a bar chart of element occurrence counts.
- save_element_type_boxplots: Creates and saves horizontal boxplots for element type counts, with optional stats and max overlays.

Assumptions and Notes:
- Figures are saved as both PDF and PNG for easy integration into LaTeX or other documents.
- Uses Matplotlib for all plotting.
- Intended for use in the ERSmeta metadata evaluation pipeline.
"""
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MaxNLocator
import matplotlib.lines as mlines
from matplotlib.patches import Patch
import matplotlib.colors as mcolors

def adjust_color_intensity(base_color, position, max_position, lighten=True):
    """
    Adjusts the intensity of a base color by blending it with white (lighten) or black (darken)
    based on the element's position in the list.

    Args:
        base_color (str or tuple): The base color (hex or RGB tuple).
        position (int): The position of the element (0-based).
        max_position (int): The maximum position (for normalization).
        lighten (bool): If True, blend with white; if False, blend with black.

    Returns:
        tuple: The adjusted RGB color.
    """
    rgb = np.array(mcolors.to_rgb(base_color))
    if lighten:
        # Blend with white
        factor = 0.4 + 0.6 * (position / max_position)  # 0.4 (lightest) to 1.0 (base)
        return tuple(rgb * factor + (1 - factor))
    else:
        # Blend with black
        factor = 1.0 - 0.6 * (position / max_position)  # 1.0 (base) to 0.4 (darkest)
        return tuple(rgb * factor)

def get_bar_color(row, max_position):
    """
    Determines the color for a bar in the histogram based on element priority and position.

    Args:
        row (pd.Series): Row from the DataFrame with 'priority' and 'position' fields.
        max_position (int): The maximum position (for normalization).

    Returns:
        tuple: The RGB color for the bar.
    """
    # Define colors for each priority
    color_map = {
        'required': '#e41a1c',      # red
        'recommended': '#377eb8',   # blue
        'optional': '#4daf4a',      # green
    }

    base_color = color_map[row['priority']]
    position = row['position']
    return adjust_color_intensity(base_color, position, max_position, lighten=True)

def save_element_histogram(df_element_counts, max_position, output_pdf_path):
    """
    Creates a horizontal bar chart showing the number of occurrences of each metadata element
    across all metadata sets. Bars are colored by priority and position.

    Args:
        df_element_counts (pd.DataFrame): DataFrame with columns 'property', 'count', 'priority', 'position'.
        max_position (int): The maximum position value for color normalization.
        output_pdf_path (str): Path to the output PDF file.

    Output:
        - Saves the figure as both PDF and PNG at the specified path.
    """
    df_element_counts['count'] = df_element_counts['count'].fillna(0)

    df_sorted = df_element_counts.sort_values(by='count', ascending=False)
    df_sorted = df_sorted[np.isfinite(df_sorted['count']) & np.isfinite(df_sorted['position'])]

    # Change 0 to 0.1 to make a visible bar
    min_bar_height = 0.1  # Small value for zero bars
    df_sorted['count'] = df_sorted['count'].apply(lambda x: min_bar_height if x == 0 else x)

    # Get colors for each bar
    df_sorted['bar_color'] = df_sorted.apply(lambda row: get_bar_color(row, max_position), axis=1)

    fig, ax = plt.subplots(figsize=(10, max(4, len(df_sorted) * 0.25)))
    bars = ax.barh(
        df_sorted['property'],
        df_sorted['count'],
        color=df_sorted['bar_color']
    )
    ax.set_xlabel('Count')
    ax.set_ylabel('Element')
    ax.set_title('Number of Occurrences of Elements over Metadata Sets')
    plt.xticks(rotation=90)

    # Annotate position to the right of each bar
    for i, (count, position) in enumerate(zip(df_sorted['count'], df_sorted['position'])):
        ax.text(
            count + 0.2,  # Slightly to the right of the bar
            i,            # y-position (row index)
            f"Pos: {position}",
            va='center',
            ha='left',
            fontsize=8,
            color='dimgray'
        )

    # Create a custom legend
    color_map = {
        'required': '#e41a1c',      # red
        'recommended': '#377eb8',   # blue
        'optional': '#4daf4a',      # green
    }

    legend_handles = [Patch(color=color, label=label.capitalize()) for label, color in color_map.items()]
    ax.legend(handles=legend_handles, title='Priority')

    plt.tight_layout()
    plt.savefig(output_pdf_path, format='pdf')
    plt.savefig(output_pdf_path.replace('.pdf', '.png'), format='png')
    plt.close()

    
def save_element_type_boxplots(
    df_element_type_counts,
    output_pdf_path,
    annotate_stats=True,
    max_series=None,
    title=None,
    xlabel="Element Count",
    ylabel="Element Type"
):
    """
    Creates horizontal boxplots for each column in df_element_type_counts and saves as a PDF.
    Optionally annotates the mean and variance next to each boxplot and overlays a vertical line
    for the maximal value per element type.

    Args:
        df_element_type_counts (pd.DataFrame): DataFrame with columns to plot (one per element type).
        output_pdf_path (str): Path to the output PDF file.
        annotate_stats (bool, optional): Whether to annotate mean and variance (default: True).
        max_series (pd.Series or dict, optional): Maximal values for each element type (column).
        title (str, optional): Title of the plot.
        xlabel (str, optional): Label for the x-axis.
        ylabel (str, optional): Label for the y-axis.

    Output:
        - Saves the figure as both PDF and PNG at the specified path.
    """
    # Fixed width, dynamic height based on number of columns (element types)
    fixed_width = 8
    row_height = 0.4  # Adjust for more/less vertical space per boxplot
    n_rows = len(df_element_type_counts.columns)
    min_height = 2
    figsize = (fixed_width, max(min_height, n_rows * row_height))

    plt.figure(figsize=figsize)
    ax = df_element_type_counts.boxplot(
        vert=False, 
        patch_artist=True,
        return_type='axes',
        showmeans=True,
        meanline=True,
        medianprops={'linewidth': 4, 'color': 'red', 'linestyle': 'solid'},
        meanprops={'linewidth': 3, 'color': 'orange', 'linestyle': 'solid'},
        )
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)    
    plt.title(title)

    # Draw red bars for maximal values if provided
    if max_series is not None:
        # Ensure max_series is a Series for consistent indexing
        if not hasattr(max_series, 'index'):
            import pandas as pd
            max_series = pd.Series(max_series)
        for i, col in enumerate(df_element_type_counts.columns):
            if col in max_series:
                max_val = max_series[col]
                # Draw a vertical red line only across the corresponding row
                # Boxplots are 1-indexed on the y-axis
                y = i + 1
                ax.vlines(
                    x=max_val,
                    ymin=y - 0.4,
                    ymax=y + 0.4,
                    colors='green',
                    linestyles='--',
                    linewidth=2,
                    alpha=0.7,
                    label='Max possible value' if i == 0 else None
                )
        
        # Only show legend once if any max_series is present
        # Create a custom vertical line for the legend
        vertical_line = mlines.Line2D([0, 0], [0, 1], color='green', linestyle='--', linewidth=2, alpha=0.7)

        # Extend x-axis if needed
        current_xlim = ax.get_xlim()
        max_max = max(max_series.max(), df_element_type_counts.max().max())
        if max_max > current_xlim[1]:
            ax.set_xlim(current_xlim[0], max_max * 1.1)
    
    # Set x-ticks to a reasonable number of natural numbers
    if max_series is not None:
        x_max = max(max_series.max(), df_element_type_counts.max().max())
    else:
        x_max = int(np.ceil(df_element_type_counts.max().max()))
    ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=8))  # Show up to 8 integer ticks
    ax.set_xlim(left=0, right=max(1, x_max * 1.1))

    if annotate_stats:
        # Annotate mean and variance for each row (now y-axis is element type)
        for i, col in enumerate(df_element_type_counts.columns):
            data = df_element_type_counts[col].dropna()
            mean = data.mean()
            var = data.var()
            #if max_series is not None and col in max_series:
                # Use the max value from max_series for annotation
            #    x_max = max_series[col]
            #else:
            #    x_max = data.max()
            # Place the annotation to the right of the boxplot
            plt.text(
                x=x_max*1.1+0.5,
                y=i+0.6,#+1.15,  # boxplots are 1-indexed on the y-axis when horizontal
                s=f"mean: {mean:.2f}\nvar: {var:.2f}",
                va='bottom',
                ha='left',
                fontsize=8
                #bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
            )

    # Create custom legend handles for mean and median
    median_line = mlines.Line2D([], [], color='red', linewidth=4, linestyle='solid', label='Median')
    mean_line = mlines.Line2D([], [], color='orange', linewidth=3, linestyle='solid', label='Mean')
    handles = [mean_line, median_line]

    if max_series is not None:
        vertical_line = mlines.Line2D([0, 0], [0, 1], color='green', linestyle='--', linewidth=2, alpha=0.7, label='Max value')
        handles.append(vertical_line)

    ax.legend(
        handles=handles,
        loc='upper center',
        bbox_to_anchor=(0.5, -0.15),  # Place legend below the axes
        ncol=len(handles),
        frameon=True
    )

    plt.tight_layout()
    plt.savefig(output_pdf_path, format='pdf')
    plt.savefig(output_pdf_path.replace('.pdf', '.png'), format='png')
    plt.close()