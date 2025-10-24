"""
Arc Position Calculations for Chord Diagrams

This module provides functions to calculate arc positions and lengths for chord diagrams
based on connection data and gap requirements.
"""

import numpy as np
import numpy.typing as npt
from typing import NamedTuple

CIRC = 2 * np.pi


class Arc(NamedTuple):
    """
    hA named tuple to store an arc's length, start and end angles all measured
     in radians
    """

    length: float
    start_angle: float
    end_angle: float


def calculate_arcs(row_sums: np.ndarray, gap_size: float) -> list[Arc]:
    """
    Calculate arc lengths, positions, and colors for a chord diagram.

    This function calculates the arc lengths proportional to the row sums,
    positions them around a circle with specified gaps between arcs,
    and assigns colors based on connection strength.

    Parameters
    ----------
    row_sums : np.ndarray
        1D numpy array containing the sum of connections for each node.
    gap_size : float
        Size of the gap between arcs in radians.

    Returns
    -------
    list[Arc]
        List of Arc namedtuple objects, each containing:
        - length: Arc length in radians
        - start_angle: Starting angle in radians
        - end_angle: Ending angle in radians

    Examples
    --------
    >>> import numpy as np
    >>> row_sums = np.array([10, 5, 3])
    >>> color_palette = ["#003f5c", "#2f4b7c", "#ffa600"]
    >>> arcs = calculate_arcs(row_sums, gap_size=0.1, color_palette=color_palette)
    >>> for arc in arcs:
    ...     print(f"Length: {arc.length:.3f}, Start: {arc.start_angle:.3f}, End: {arc.end_angle:.3f}, Color: {arc.fill_color}")
    """

    # Calculate the portion of the circumference occupied by gaps
    n = len(row_sums)
    total_gap = gap_size * (n - 1)

    # From the remainder, map row_sums into proportional arc lengths
    total_weight = np.sum(row_sums)
    arc_lengths = (CIRC - total_gap) * row_sums / total_weight

    # Calculate the angles at the edges of the arcs
    arcs: list[Arc] = []
    current_angle = 0.0

    for i in range(n):
        end_angle = current_angle + arc_lengths[i]
        arcs.append(
            Arc(
                length=arc_lengths[i],
                start_angle=current_angle,
                end_angle=end_angle,
            )
        )
        current_angle = end_angle + gap_size  # Move to next position, adding gap

    return arcs


def arc_coordinates(
    radius: float, arc: Arc, num_points: int
) -> npt.NDArray[np.float64]:
    """
    Generate points for a circular arc.

    This function takes the radius and an Arc object containing start and end angles,
    then returns the coordinates of points along that arc expressed as complex
    numbers. It uses Euler's formula from complex analysis: e^(iθ) = cos(θ) + i × sin(θ).

    Parameters
    ----------
    radius : float
        Radius of the arc
    arc : Arc
        Arc namedtuple containing:
        - length: Arc length in radians (used for point density calculation)
        - start_angle: Starting angle in radians
        - end_angle: Ending angle in radians
    num_points : int
        Base number of points for a full circle (2π arc)

    Returns
    -------
    np.ndarray
        Complex array representing points along the arc, where:
        - Real part = radius * cos(θ) (x-coordinate)
        - Imaginary part = radius * sin(θ) (y-coordinate)

    Examples
    --------
    >>> import numpy as np
    >>> from collections import namedtuple
    >>> Arc = namedtuple('Arc', ['length', 'start_angle', 'end_angle'])
    >>> arc = Arc(length=np.pi/2, start_angle=0, end_angle=np.pi/2)
    >>> points = arc_coordinates(1.0, arc)
    >>> # A π/2 arc (quarter circle) will have 12-13 points (50 * (π/2) / (2π) = 12.5)
    """

    # Generate intermediary points between the edges of the arc
    theta = np.linspace(
        arc.start_angle, arc.end_angle, round(num_points * arc.length / CIRC)
    )
    return radius * np.exp(1j * theta)
