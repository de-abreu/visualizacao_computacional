"""
Ribbon Calculations for Chord Diagrams

This module provides functions to calculate ribbon positions, control points,
and create ribbon shapes for chord diagrams that connect arcs.
"""

import numpy as np
import numpy.typing as npt
from typing import NamedTuple
from plotly.graph_objects import Scatter
from .shapes import ShapeStyle, assign_color, create_hover, create_shape
from .ideograms import Ideogram
from .arcs import Arc, arc_coordinates
from .colors import hex_to_rgba


class Point(NamedTuple):
    x: float
    y: float


class Ribbon(NamedTuple):
    top_edge: tuple[Point, ...]  # Control points for top edge
    bottom_edge: tuple[Point, ...]  # Control points for bottom edge
    from_arc: Arc
    to_arc: Arc
    fill_color: str


class Connection(NamedTuple):
    ribbon: Ribbon
    from_ideo: Ideogram
    to_ideo: Ideogram
    value: float | int


def calculate_ribbon_ends(
    mapped_data: npt.NDArray[np.number],
    ideograms: list[Ideogram],
    permutations: npt.NDArray[np.integer],
) -> list[list[Arc | None]]:
    """
    Compute the ribbon end positions for all ideograms and connections.

    This function calculates the precise angular positions where ribbons
    should start and end on each arc. For each arc, it creates a sequence
    of boundaries that partition the arc into segments corresponding to
    connections with other entities.

    Parameters
    ----------
    mapped_data : np.ndarray
        Mapped connection data where mapped_data[i,j] contains the angular
        length allocated for the connection from entity i to entity j
    arcs : list[Arc]
        List of Arc objects containing start and end angles for each arc
    permutations : np.ndarray
        Sorting indices for the mapped data, where permutations[i] contains
        the indices of connections sorted by their mapped length

    Returns
    -------
    list[list[tuple[float, float]]]
        A list of lists where:
        - Outer list index corresponds to arc index
        - Inner list contains tuples of (start_angle, end_angle) for each
          ribbon segment on that arc, ordered by the sorted connection indices
        - Each tuple represents the angular span of a ribbon connection
          on the arc, with angles in radians

    Notes
    -----
    The ribbon_boundaries array has shape (n, n+1) where n is the number
    of arcs. This accounts for:
    - n arcs (first dimension)
    - n+1 boundaries per arc: start angle + n ribbon segment boundaries
    """

    ideogram_count = len(ideograms)
    ribbon_ends: list[list[Arc | None]] = []

    for row in range(ideogram_count):
        ideo_ribbons_ends = []
        start_angle = ideograms[row].arc.start_angle
        col = 0

        # permutations[row][col] picks the col'th column with the lowest value.
        # This first loop effectively skips all columns with value 0 (no
        # connection to another ideogram.
        while col < ideogram_count and mapped_data[row][permutations[row][col]] == 0:
            ideo_ribbons_ends.append(None)
            col += 1

        # Then all arcs with a length is added from the shortest to the greatest
        for col in range(col, ideogram_count):
            arc_length = mapped_data[row][permutations[row][col]]
            end_angle = start_angle + arc_length
            ideo_ribbons_ends.append(Arc(arc_length, start_angle, end_angle))
            start_angle = end_angle
        ribbon_ends.append(ideo_ribbons_ends)

    return ribbon_ends


def calculate_control_points(
    angles: tuple[float, float, float], radius: float
) -> tuple[Point, ...]:
    """
    Calculate control points for Bezier curves.

    Parameters
    ----------
    angle : List[float]
        A 3-list containing angular coordinates of the control points b0, b1, b2
    radius : float
        The distance from b1 to the origin O(0,0) of the polar system of
        coordinates. It is used to scale the midpoint creating a "bulge" effect

    Returns
    -------
    List[Point]
        List of Point objects for the control points
    """

    b_cplx = np.array([np.exp(1j * angles[i]) for i in range(3)], dtype=np.complex128)
    b_cplx[1] *= radius

    return tuple(Point(x, y) for x, y in zip(b_cplx.real, b_cplx.imag))


def calculate_connections(
    matrix: npt.NDArray[np.floating | np.integer],
    row_sums: npt.NDArray[np.integer | np.floating],
    ideograms: list[Ideogram],
    radius: float,
    color_palette: list[str],
) -> list[Connection]:
    """
    Calculate ribbon control points for connecting arcs in a chord diagram.

    This function takes the connection matrix and arc positions, then calculates
    the Bezier control points for all ribbons that connect the arcs.

    Parameters
    ----------
    matrix : npt.NDArray[np.floating | np.integer]
        Connection matrix where [i,j] contains the connection strength
        from entity i to entity j
    arcs : list[Arc]
        List of Arc objects containing arc lengths and positions

    Returns
    -------
    list[Ribbon]
        List of Ribbon objects containing control points for all connections
    """

    # Pick the maximum row_sum value to normalize the color selection for the
    # ribbons
    max_sum = row_sums.max()

    # Extract arc lengths and start angles
    arc_lengths = np.array([ideo.arc.length for ideo in ideograms])

    # Map ribbons to arc lengths
    connection_ends_mapping = np.zeros(matrix.shape, dtype=np.float64)
    for j in range(matrix.shape[0]):
        connection_ends_mapping[:, j] = arc_lengths * matrix[:, j] / row_sums

    # Sort indices so that ribbons are placed on the arcs ordered from those
    # with the smallest to those with the greatest length
    permutations = np.argsort(connection_ends_mapping, axis=1)

    # Calculate ribbon end positions
    connection_ends = calculate_ribbon_ends(
        connection_ends_mapping, ideograms, permutations
    )

    # Precompute inverse permutations
    inverse_permutations = np.zeros_like(permutations)
    for row in range(inverse_permutations.shape[0]):
        for permutated_position, original_index in enumerate(permutations[row]):
            inverse_permutations[row][original_index] = permutated_position

    # Check if matrix is symmetric to avoid duplicate connections
    is_symmetric = np.allclose(matrix, matrix.T)

    # Create ribbon control points
    connections: list[Connection] = []
    n = len(ideograms)

    for i in range(n):
        inverse_perm_i = inverse_permutations[i]

        # If matrix is symmetric, only iterate over upper triangle (including diagonal)
        # Otherwise, iterate over all elements
        for j in range(i, n) if is_symmetric else range(n):
            # Skip when there's no connection
            if matrix[i, j] == 0:
                continue

            # Get the arc for entity i's connection with j
            arc_i = connection_ends[i][inverse_perm_i[j]]

            # Get arc for entity j's connection with i
            inverse_perm_j = inverse_permutations[j]
            arc_j = connection_ends[j][inverse_perm_j[i]]

            # For regular connections, reverse the second arc ends to prevent twisting
            if arc_i != arc_j:
                arc_j = Arc(arc_j.length, arc_j.end_angle, arc_j.start_angle)

            # Calculate the ribbon's control points and add ribbon to the list
            connections.append(
                Connection(
                    ribbon=Ribbon(
                        top_edge=(
                            calculate_control_points(
                                (
                                    arc_i.start_angle,
                                    (arc_i.start_angle + arc_j.start_angle) / 2,
                                    arc_j.start_angle,
                                ),
                                radius,
                            )
                        ),
                        bottom_edge=(
                            calculate_control_points(
                                (
                                    arc_i.end_angle,
                                    (arc_i.end_angle + arc_j.end_angle) / 2,
                                    arc_j.end_angle,
                                ),
                                radius,
                            )
                        ),
                        from_arc=arc_i,
                        to_arc=arc_j,
                        fill_color=assign_color(matrix[i, j], max_sum, color_palette),
                    ),
                    from_ideo=ideograms[i],
                    to_ideo=ideograms[j],
                    value=matrix[i][j],
                )
            )
    return connections


def bezier_curve(control_points: tuple[Point, ...]) -> str:
    """
    Generates a Plotly SVG path string for a quadratic Bezier curve.

    Creates the SVG path data for a quadratic Bezier curve defined by three
    control points in the format required by Plotly's shape objects.

    Parameters
    ----------
    control_points : List[Tuple[float, float]]
        A list of exactly three control points that define the Bezier curve.
        Each point is a tuple of (x, y) coordinates.
        - control_points[0]: Start point of the curve
        - control_points[1]: Control point that defines the curve's shape
        - control_points[2]: End point of the curve

    Returns
    -------
    str
        SVG path string in the format:
        "M x0,y0 Q x1,y1 x2,y2"
        Where:
        - M: Move to start point
        - Q: Quadratic Bezier curve with control point and end point

    Raises
    ------
    ValueError
        If control_points does not contain exactly three points.
    """

    start_point, control_point, end_point = control_points

    return (
        f"M {start_point.x},{start_point.y} "
        f"Q {control_point.x}, {control_point.y} "
        f"{end_point.x}, {end_point.y}"
    )


def create_connections(
    connections: list[Connection],
    num_points: int,
    text_template: str,
    radius: float,
) -> tuple[list[ShapeStyle], list[Scatter]]:
    """
    Create all ribbon shapes and hover data from pre-calculated ribbon control points.

    This function takes pre-calculated Ribbon objects containing control points
    and converts them into visual shapes and hover interactions for the chord diagram.

    Parameters
    ----------
    ribbons : List[Ribbon]
        List of Ribbon objects containing control points for all connections
    labels : List[str]
        Labels for each entity
    text_template : str
        Template for ribbon hover text. Available placeholders:
        - {origin}: The label where the ribbon originates
        - {destination}: The label the ribbon ends at
        - {value}: The weight/value of that connection

    Returns
    -------
    luple[list[ShapeStyle], list[Scatter]]
        Tuple containing:
        - List of ribbon shapes
        - List of hover data scatter objects
    """
    shapes: list[ShapeStyle] = []
    hovers: list[Scatter] = []

    for connection in connections:
        ribbon = connection.ribbon
        from_arc_coords = arc_coordinates(radius, ribbon.from_arc, num_points)
        to_arc_coords = arc_coordinates(radius, ribbon.to_arc, num_points)

        # Create SVG path for the ribbon using the control points
        # The ribbon consists of two Bezier curves (top and bottom edges)
        # connected by circular arcs at the ends
        svg_path = (
            # Top edge Bezier curve
            bezier_curve(ribbon.top_edge)
            +
            # Circular arc along the end arc (from end of top edge to start of bottom edge)
            f"L {to_arc_coords.real}, {to_arc_coords.imag}"
            +
            # Bottom edge Bezier curve (reversed to create closed shape)
            bezier_curve(ribbon.bottom_edge[::-1])
            +
            # Circular arc along the start arc (from end of bottom edge back to start of top edge)
            f"L {from_arc_coords.real}, {from_arc_coords.imag}"
        )

        transparent_fill = hex_to_rgba(ribbon.fill_color, 0.75)
        # Create the ribbon shape
        shapes.append(create_shape(svg_path, transparent_fill))
        from_ideo = connection.from_ideo
        to_ideo = connection.to_ideo
        hovers += [
            create_hover(
                from_arc_coords.real,
                from_arc_coords.imag,
                text_template.format(
                    origin=from_ideo.label,
                    destination=to_ideo.label,
                    value=connection.value,
                ),
                ribbon.fill_color,
            ),
            create_hover(
                to_arc_coords.real,
                to_arc_coords.imag,
                text_template.format(
                    origin=to_ideo.label,
                    destination=from_ideo.label,
                    value=connection.value,
                ),
                ribbon.fill_color,
            ),
        ]

    return shapes, hovers
