"""
Chord Diagram Visualization Module

This module provides functionality to create interactive chord diagrams using Plotly.
Chord diagrams visualize relationships between entities, where the width of ribbons
represents the strength of connections between nodes.
"""

import numpy as np
import numpy.typing as npt
import plotly.graph_objects as go

from chord_diagram.utils.ideograms import calculate_ideograms, create_ideograms

from .utils.spectral_ordering import spectral_order
from .utils.arcs import CIRC, calculate_arcs, create_arcs


def chord_diagram(
    matrix: npt.NDArray[np.floating | np.integer],
    title: str = "Chord diagram",
    labels: list[str] | None = None,
    gap_fraction: float = 0.0,
    color_palette: list[str] | None = None,
    arc_hover_template: str = "{label}:<br>{total} connections",
    ribbon_hover_template: str = "{origin} → {destination}: {value}",
    size: int = 600,
    num_points: int = 50,
) -> go.Figure:
    """
    Create an interactive chord diagram visualization.

    Parameters
    ----------
    matrix : np.ndarray
        A n x n numpy matrix containing integer or floating point values representing
        the connections between entities. The matrix should be symmetric for
        undirected relationships.

    gap_fraction : float, default = 0.005
        Fraction of the total circle (2π) to use as gap between arcs.
        For example, 0.005 means 0.5% of the circle will be gaps.

        Its value should be equal or greater than zero, and low enough so that
        (n - 1) ✕ gap ✕ 2π < 2π.

    labels : list[str] | None, default = None
        A list of strings to serve as labels for the arcs in the ideogram.
        If None, generic labels will be generated.

    color_palette : list[str] | None, default = None
        A list of hex color values to serve as a color palette for the chord diagram.
        If None, a default color palette will be used.

    arc_hover_template : str, default = "{label}: {total} connections"
        Template for the message displayed when hovering over arcs.
        Available placeholders:
        - {label}: The label name
        - {total}: The sum value of connections for this label

    ribbon_hover_template : str, default = "{origin} → {destination}: {value}"
        Template for the message displayed when hovering over ribbons.
        Available placeholders:
        - {origin}: The label where the ribbon originates
        - {destination}: The label the ribbon ends at
        - {value}: The weight/value of that connection

    size : int, default = 600
        Image width and height, in pixels

    num_points : int, default=50
        Base number of points to draw a full circle (2π arc). The higher the
        quantity, the smoother is the circumference with an added computation
        time.


    Returns
    -------
    go.Figure
        A Plotly Figure object containing the chord diagram visualization.

    Raises
    ------
    ValueError
        - If matrix is not 2D or not square or contains negative values
        - If labels length doesn't match matrix dimensions
        - If the gap fraction is set to a value that is too great or negative

    Examples
    --------
    >>> import numpy as np
    >>> matrix = np.array([[0, 5, 3], [5, 0, 2], [3, 2, 0]])
    >>> labels = ['A', 'B', 'C']
    >>> fig = draw_chord_diagram(matrix, labels)
    >>> fig.show()
    """

    # Validate matrix
    if matrix.ndim != 2:
        raise ValueError("Matrix must have 2 dimensions")
    n, m = matrix.shape[0], matrix.shape[1]
    if n != m:
        raise ValueError(f"Matrix must be square, current dimensions are: {n} × {m}")
    if np.any(matrix < 0):
        raise ValueError("Matrix must not contain negative values")

    # Validate labels
    if labels is None:
        labels = [f"Node {i + 1}" for i in range(n)]
    if len(labels) != matrix.shape[0]:
        raise ValueError("Number of labels must match matrix dimensions")

    # Validate gap fraction
    if not 0 <= gap_fraction < 1:
        raise ValueError(
            "gap_fraction must be a value equal or greater than 0 and lesser than 1"
        )
    gap_size = CIRC * gap_fraction
    total_gap = gap_size * (n - 1)
    if total_gap >= CIRC:
        raise ValueError(
            f"Total gap space {total_gap} exceeds available circle space {CIRC}"
        )

    # If dataset is empty (all row sums are zero) return an empty plot with the
    # "Dataset is empty" message
    row_sums = np.atleast_1d(np.sum(matrix, axis=1, dtype=np.float64))
    hide = {"showgrid": False, "zeroline": False, "showticklabels": False, "title": ""}
    if np.sum(row_sums) == 0:
        fig = go.Figure()
        _ = fig.add_annotation(
            text="Dataset is empty",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            xanchor="center",
            yanchor="middle",
            showarrow=False,
            font={"size": 20, "color": "red"},
        )
        _ = fig.update_layout(
            title="Empty Dataset",
            showlegend=False,
            xaxis=hide,
            yaxis=hide,
            width=size,
            height=size,
        )
        return fig

    # Set default color palette if not provided
    if not color_palette:
        color_palette = [
            "#003f5c",
            "#2f4b7c",
            "#665191",
            "#a05195",
            "#d45087",
            "#f95d6a",
            "#ff7c43",
            "#ffa600",
        ]

    # Reorder the matrix so as to minimize ribbon crossover
    matrix, labels = spectral_order(matrix, labels)

    # Calculate the arcs' geometry and colors from the data, store their shape
    # and hover data
    ideograms = calculate_ideograms(row_sums, gap_size, color_palette)
    ideo_shapes, ideo_hovers = create_ideograms(
        ideograms,
        labels,
        num_points,
        arc_hover_template,
    )

    # TODO: Continue implementing the core chord diagram logic here
    # This will include:
    # 3. Generating ribbons between arcs based on matrix values
    # 4. Setting up hover interactions
    # 5. Creating the final Plotly figure

    # Placeholder implementation - to be replaced with actual chord diagram logic
    fig = go.Figure()

    # Add a simple message indicating this is a skeleton
    fig.add_annotation(
        text="Chord Diagram Skeleton - Implementation in Progress",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        xanchor="center",
        yanchor="middle",
        showarrow=False,
        font={"size": 16},
    )

    # Set layout properties
    fig.update_layout(
        title="Chord Diagram",
        showlegend=False,
        xaxis=hide,
        yaxis=hide,
        width=size,
        height=size,
    )

    return fig
