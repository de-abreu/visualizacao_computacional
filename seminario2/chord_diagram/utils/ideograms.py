"""
Arc Position Calculations for Chord Diagrams

This module provides functions to calculate arc positions and lengths for chord diagrams
based on connection data and gap requirements.
"""

import numpy as np
from typing import NamedTuple
from .shapes import ShapeStyle, assign_color, create_hover, create_shape
from .arcs import Arc, arc_coordinates, calculate_arcs
from plotly.graph_objects import Scatter


class Ideogram(NamedTuple):
    arc: Arc
    value: float | int
    label: str
    fill_color: str


def calculate_ideograms(
    row_sums: np.ndarray, labels: list[str], gap_size: float, color_palette: list[str]
) -> list[Ideogram]:
    arcs = calculate_arcs(row_sums, gap_size)
    max_sum = row_sums.max()

    return [
        Ideogram(
            arcs[i],
            row_sums[i],
            labels[i],
            assign_color(row_sums[i], max_sum, color_palette),
        )
        for i in range(len(arcs))
    ]


def create_ideograms(
    ideograms: list[Ideogram],
    num_points: int,
    text_template: str,
    inner_radius: float,
    ideogram_width: float = 0.1,
) -> tuple[list[ShapeStyle], list[Scatter]]:
    """
    Create arc shapes and hover data for the chord diagram.

    This function generates the visual representation of arcs (ideograms) in the
    chord diagram, including their shapes, colors, and hover interactions.
    Each arc represents an entity in the dataset, with its length proportional
    to the entity's total connections.

    Parameters
    ----------
    arcs : list[Arc]
        List of Arc namedtuple objects containing:
        - length: Arc length in radians
        - start_angle: Starting angle in radians
        - end_angle: Ending angle in radians
    labels : list[str]
        Labels for each entity/arc
    row_sums : np.ndarray
        1D array containing the sum of connections for each entity.
        Used for color normalization and hover text.
    num_points : int
        Base number of points for arc approximation. Higher values
        result in smoother arcs but increased computational cost.
    text_template : str
        Template string for hover text. Should contain placeholders:
        - {label}: Will be replaced with entity label
        - {total}: Will be replaced with total connections
        Example: "{label}: {total} connections"
    color_palette : list[str]
        List of color strings (hex, rgb, or named colors) for arc coloring.
        Colors are assigned based on normalized connection strength.
    outer_radius : float, optional
        Outer radius of the arcs. Defaults to 1.1.
    inner_radius : float, optional
        Inner radius of the arcs. Defaults to 1.0.

    Returns
    -------
    tuple[list[ShapeStyle], list[Scatter]]
        A tuple containing:
        - List of ShapeStyle objects for arc visualization
        - List of Scatter objects for hover interactions

    Examples
    --------
    >>> import numpy as np
    >>> from chord_diagram.utils.arcs import Arc, create_arcs
    >>>
    >>> # Create sample data
    >>> arcs = [Arc(length=np.pi/2, start_angle=0, end_angle=np.pi/2),
    ...         Arc(length=np.pi/3, start_angle=np.pi/2, end_angle=5*np.pi/6)]
    >>> labels = ["Entity A", "Entity B"]
    >>> row_sums = np.array([100, 50])
    >>> color_palette = ["#003f5c", "#ffa600"]
    >>>
    >>> # Create arcs with hover data
    >>> shapes, hovers = create_arcs(
    ...     arcs=arcs,
    ...     labels=labels,
    ...     row_sums=row_sums,
    ...     num_points=50,
    ...     text_template="{label}: {total} connections",
    ...     color_palette=color_palette
    ... )

    Notes
    -----
    - Arc colors are determined by normalizing row_sums to the maximum value
      and mapping to the provided color palette
    - The SVG path for each arc is constructed by connecting outer and inner
      arc coordinates in a closed loop
    - Hover text is positioned along the outer arc for optimal visibility
    """
    shapes: list[ShapeStyle] = []
    hovers: list[Scatter] = []

    for ideo in ideograms:
        # Generate coordinates for outer and inner arcs
        inner_arc_coords = arc_coordinates(inner_radius, ideo.arc, num_points)
        outer_arc_coords = arc_coordinates(
            inner_radius + ideogram_width, ideo.arc, num_points
        )

        # Build SVG path that connects outer and inner arcs
        svg_path = "M "

        # Add outer arc points
        for point_index in range(len(outer_arc_coords)):
            arc_coords = outer_arc_coords[point_index]
            svg_path += f"{arc_coords.real}, {arc_coords.imag} L "

        # Reverse inner arc coordinates to create a closed shape
        reversed_inner_coords = inner_arc_coords[::-1]

        # Add inner arc points
        for point_index in range(len(reversed_inner_coords)):
            arc_coords = reversed_inner_coords[point_index]
            svg_path += f"{arc_coords.real}, {arc_coords.imag} L "

        # Close the path by returning to the starting point
        svg_path += f"{outer_arc_coords.real}, {outer_arc_coords.imag}"

        shapes.append(create_shape(svg_path, ideo.fill_color))
        hovers.append(
            create_hover(
                outer_arc_coords.real,
                outer_arc_coords.imag,
                text_template.format(label=ideo.label, total=ideo.value),
                ideo.fill_color,
            )
        )

    return shapes, hovers
