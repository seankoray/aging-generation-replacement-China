"""
Publication-Quality Plotting Module

A reusable module for creating publication-quality figures.

Usage:
    from plot_style import Figure, COLORS

    # Create a single plot
    fig = Figure(figsize=(8, 5))
    ax = fig.get_ax()
    ax.plot(x, y, color=COLORS['blue'], marker='o')
    fig.save('output.pdf')

    # Create multiple subplots
    fig = Figure(figsize=(15, 4), nrows=1, ncols=5, sharey=True)
    axes = fig.get_axes()
    for ax in axes:
        ax.plot(x, y)
    fig.save('output.pdf')
"""

import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Tuple, Optional, Union
import numpy as np

# ============================================
# STYLE SETTINGS
# ============================================

def _apply_style():
    """Apply publication-quality style settings globally."""
    plt.rcParams.update({
        'font.family': 'Arial',
        'font.size': 9,
        'axes.linewidth': 0.8,
        'axes.edgecolor': 'black',
        'axes.facecolor': 'white',
        'axes.spines.top': False,
        'axes.spines.right': False,
        'grid.alpha': 0.2,
        'grid.linewidth': 0.5,
        'xtick.major.size': 3,
        'ytick.major.size': 3,
        'xtick.minor.size': 0,
        'ytick.minor.size': 0,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        'legend.frameon': False,
        'legend.fontsize': 8,
        'figure.dpi': 150,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.05,
    })

# Apply on module import
_apply_style()


# ============================================
# COLOR PALETTES
# ============================================

COLORS = {
    'blue': '#3B82F6',
    'red': '#EF4444',
    'green': '#10B981',
    'orange': '#F59E0B',
    'purple': '#8B5CF6',
    'cyan': '#06B6D4',
    'pink': '#EC4899',
    'gray': '#6B7280',
    'dark_gray': '#374151',
    'light_gray': '#D1D5DB',
}

# Sequential color palette for heatmaps, stacked bars, etc.
SEQUENTIAL_COLORS = [
    '#D1E8FF',  # Very light blue
    '#93C5FD',  # Light blue
    '#60A5FA',  # Blue
    '#3B82F6',  # Darker blue
    '#2563EB',  # Deep blue
    '#1D4ED8',  # Very dark blue
]

# Categorical color palette for grouping categories
CATEGORICAL_COLORS = [
    '#3B82F6',  # Blue
    '#EF4444',  # Red
    '#10B981',  # Green
    '#F59E0B',  # Orange
    '#8B5CF6',  # Purple
    '#06B6D4',  # Cyan
    '#EC4899',  # Pink
    '#6B7280',  # Gray
]

# Diverging color palette for positive/negative values
DIVERGING_COLORS = ['#EF4444', '#F59E0B', '#FCD34D', '#10B981', '#059669']


# ============================================
# LINE STYLES
# ============================================

LINE_STYLES = {
    'solid': '-',
    'dashed': '--',
    'dotted': ':',
    'dashdot': '-.',
}

MARKERS = {
    'circle': 'o',
    'square': 's',
    'triangle': '^',
    'diamond': 'D',
    'cross': 'x',
    'plus': '+',
    'star': '*',
}


# ============================================
# MAIN FIGURE CLASS
# ============================================

class Figure:
    """
    Main figure class for creating publication-quality plots.

    Parameters
    ----------
    figsize : tuple, optional
        Figure size (width, height) in inches. Default is (8, 5).
    nrows : int, optional
        Number of subplot rows. Default is 1.
    ncols : int, optional
        Number of subplot columns. Default is 1.
    sharex : bool or str, optional
        Share x-axis among subplots. Default is False.
    sharey : bool or str, optional
        Share y-axis among subplots. Default is False.
    tight_layout : bool, optional
        Use tight_layout. Default is True.
    """

    def __init__(self, figsize: Tuple[float, float] = (8, 5),
                 nrows: int = 1, ncols: int = 1,
                 sharex: Union[bool, str] = False,
                 sharey: Union[bool, str] = False,
                 tight_layout: bool = True):

        self.figsize = figsize
        self.nrows = nrows
        self.ncols = ncols
        self.tight_layout = tight_layout

        # Create figure and axes
        self.fig, self.axes = plt.subplots(
            nrows=nrows, ncols=ncols,
            figsize=figsize,
            sharex=sharex,
            sharey=sharey,
        )

        # Ensure axes is always a list
        if nrows * ncols == 1:
            self.axes = [self.axes]

        self.legend_handles = []
        self.legend_labels = []

    def get_ax(self, index: int = 0) -> plt.Axes:
        """Get a specific axes object."""
        return self.axes[index]

    def get_axes(self) -> List[plt.Axes]:
        """Get all axes objects."""
        return self.axes

    def add_legend_item(self, handle, label: str):
        """Add an item to the legend."""
        self.legend_handles.append(handle)
        self.legend_labels.append(label)

    def set_labels(self, xlabel: str = None, ylabel: str = None,
                   title: str = None, ax_index: int = 0):
        """Set axis labels and title."""
        ax = self.get_ax(ax_index)
        if xlabel:
            ax.set_xlabel(xlabel)
        if ylabel:
            ax.set_ylabel(ylabel)
        if title:
            ax.set_title(title, pad=10)

    def set_xlim(self, xlim: Tuple[float, float], ax_index: int = 0):
        """Set x-axis limits."""
        self.get_ax(ax_index).set_xlim(xlim)

    def set_ylim(self, ylim: Tuple[float, float], ax_index: int = 0):
        """Set y-axis limits."""
        self.get_ax(ax_index).set_ylim(ylim)

    def set_xticks(self, ticks, ax_index: int = 0, labels=None):
        """Set x-axis ticks."""
        ax = self.get_ax(ax_index)
        ax.set_xticks(ticks)
        if labels is not None:
            ax.set_xticklabels(labels)

    def set_yticks(self, ticks, ax_index: int = 0, labels=None):
        """Set y-axis ticks."""
        ax = self.get_ax(ax_index)
        ax.set_yticks(ticks)
        if labels is not None:
            ax.set_yticklabels(labels)

    def add_grid(self, axis: str = 'y', ax_index: int = 0):
        """Add grid lines."""
        self.get_ax(ax_index).grid(True, axis=axis, alpha=0.2, linewidth=0.5)

    def add_legend(self, position: str = 'bottom', ncol: int = None,
                   bbox_to_anchor: Tuple[float, float] = None):
        """
        Add legend to the figure.

        Parameters
        ----------
        position : str
            Legend position: 'bottom', 'top', 'left', 'right', or 'outside'
        ncol : int, optional
            Number of columns in the legend.
        bbox_to_anchor : tuple, optional
            Custom bbox_to_anchor for legend placement.
        """
        if not self.legend_handles:
            return

        # Default positions
        positions = {
            'bottom': {'loc': 'lower center', 'bbox_to_anchor': (0.5, -0.05)},
            'top': {'loc': 'upper center', 'bbox_to_anchor': (0.5, 1.05)},
            'left': {'loc': 'center left', 'bbox_to_anchor': (-0.1, 0.5)},
            'right': {'loc': 'center right', 'bbox_to_anchor': (1.05, 0.5)},
            'outside': {'loc': 'center left', 'bbox_to_anchor': (1.02, 0.5)},
        }

        pos = positions.get(position, positions['bottom'])
        if bbox_to_anchor:
            pos['bbox_to_anchor'] = bbox_to_anchor

        # Determine ncol
        if ncol is None:
            if position == 'bottom' or position == 'top':
                ncol = min(len(self.legend_handles), 5)
            else:
                ncol = 1

        self.fig.legend(
            self.legend_handles,
            self.legend_labels,
            loc=pos['loc'],
            bbox_to_anchor=pos['bbox_to_anchor'],
            ncol=ncol,
            frameon=False,
        )

    def adjust_margins(self, left: float = None, right: float = None,
                       bottom: float = None, top: float = None):
        """Adjust figure margins."""
        params = {}
        if left is not None:
            params['left'] = left
        if right is not None:
            params['right'] = right
        if bottom is not None:
            params['bottom'] = bottom
        if top is not None:
            params['top'] = top
        if params:
            self.fig.subplots_adjust(**params)

    def save(self, filepath: Union[str, Path], dpi: int = 300,
             formats: List[str] = None, close: bool = True):
        """
        Save figure to file.

        Parameters
        ----------
        filepath : str or Path
            Output file path.
        dpi : int
            Resolution in dots per inch. Default is 300.
        formats : list of str, optional
            Additional formats to save (e.g., ['png']).
        close : bool
            Close the figure after saving. Default is True.
        """
        filepath = Path(filepath)
        self.fig.savefig(filepath, dpi=dpi, bbox_inches='tight')

        # Save additional formats if specified
        if formats:
            base = filepath.stem
            for fmt in formats:
                self.fig.savefig(
                    filepath.parent / f"{base}.{fmt}",
                    dpi=dpi,
                    bbox_inches='tight',
                )

        if self.tight_layout:
            self.fig.tight_layout()

        if close:
            plt.close(self.fig)

    def show(self):
        """Display the figure."""
        if self.tight_layout:
            self.fig.tight_layout()
        plt.show()

    def close(self):
        """Close the figure."""
        plt.close(self.fig)


# ============================================
# CONVENIENCE FUNCTIONS
# ============================================

def plot_line(x, y, color: str = None, linestyle: str = '-',
               marker: str = None, linewidth: float = 1.5,
               markersize: float = 4, label: str = None,
               ax: plt.Axes = None) -> plt.Axes:
    """
    Plot a line with publication-quality style.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes object.
    """
    if color is None:
        color = COLORS['blue']

    if ax is None:
        fig = Figure()
        ax = fig.get_ax()

    line, = ax.plot(x, y, color=color, linestyle=linestyle,
                    marker=marker, linewidth=linewidth,
                    markersize=markersize, label=label)

    ax.grid(True, axis='y', alpha=0.2, linewidth=0.5)

    return ax


def plot_bar(x, height, color: str = None, alpha: float = 0.6,
             width: float = 0.8, label: str = None,
             ax: plt.Axes = None) -> plt.Axes:
    """
    Plot a bar chart with publication-quality style.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes object.
    """
    if color is None:
        color = COLORS['blue']

    if ax is None:
        fig = Figure()
        ax = fig.get_ax()

    bars = ax.bar(x, height, color=color, alpha=alpha, width=width, label=label)
    ax.grid(True, axis='y', alpha=0.2, linewidth=0.5)

    return ax


def plot_stacked_bar(x, heights: List[np.ndarray], colors: List[str] = None,
                     labels: List[str] = None, ax: plt.Axes = None) -> plt.Axes:
    """
    Plot a stacked bar chart with publication-quality style.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes object.
    """
    if colors is None:
        colors = SEQUENTIAL_COLORS[:len(heights)]

    if ax is None:
        fig = Figure()
        ax = fig.get_ax()

    bottom = np.zeros_like(x) if x is not None else None
    handles = []

    for h, color, label in zip(heights, colors, labels or [None] * len(heights)):
        h_arr = np.array(h) if not isinstance(h, np.ndarray) else h
        bars = ax.bar(x, h_arr, bottom=bottom, color=color,
                      width=3, label=label, edgecolor='white', linewidth=0.3)
        bottom += h_arr
        handles.append(bars)

    ax.grid(True, axis='y', alpha=0.2, linewidth=0.5)

    return ax


def plot_scatter(x, y, color: str = None, alpha: float = 0.6,
                 s: float = 20, label: str = None,
                 ax: plt.Axes = None) -> plt.Axes:
    """
    Plot a scatter plot with publication-quality style.

    Returns
    -------
    ax : matplotlib.axes.Axes
        The axes object.
    """
    if color is None:
        color = COLORS['blue']

    if ax is None:
        fig = Figure()
        ax = fig.get_ax()

    scat = ax.scatter(x, y, color=color, alpha=alpha, s=s, label=label)
    ax.grid(True, axis='y', alpha=0.2, linewidth=0.5)

    return ax
