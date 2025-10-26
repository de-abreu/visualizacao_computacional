import numpy as np
import numpy.typing as npt
from re import match


def validate_matrix(
    matrix: npt.NDArray[np.floating | np.integer],
) -> int:
    """
    Validate the input matrix for arc diagram requirements.

    Parameters
    ----------
    matrix : npt.NDArray[np.floating | np.integer]
        Input matrix to validate

    Returns
    -------
    int
        Matrix dimension (number of rows/columns)

    Raises
    ------
    ValueError
        If matrix is not 2D, contains negative values, or is not symmetric
    """
    if matrix.ndim != 2:
        raise ValueError("Matrix must have 2 dimensions")
    if np.any(matrix < 0):
        raise ValueError("Matrix must not contain negative values")
    if not np.allclose(matrix, matrix.T):
        raise ValueError("Matrix must be symmetric")
    return matrix.shape[0]


def validate_labels(labels: list[str] | None, length: int) -> list[str]:
    """
    Validate and process labels for the arc diagram.

    Parameters
    ----------
    labels : list[str] | None
        Labels for each node, or None to generate default labels
    length : int
        Expected number of labels (matrix dimension)

    Returns
    -------
    list[str]
        Validated labels list

    Raises
    ------
    ValueError
        If number of labels doesn't match matrix dimensions
    """
    if labels is None:
        return [f"Node {i + 1}" for i in range(length)]
    if len(labels) == length:
        return labels
    raise ValueError("Number of labels must match matrix dimensions")


def validate_colors(color_palette: list[str] | None) -> list[str]:
    """
    Validate and process color palette for the arc diagram.

    Parameters
    ----------
    color_palette : list[str] | None
        Color palette to validate, or None to use default colors

    Returns
    -------
    list[str]
        Validated color palette

    Raises
    ------
    ValueError
        If any color is not a valid hexadecimal color code
    """
    if color_palette is None:
        return [
            "#003f5c",
            "#2f4b7c",
            "#665191",
            "#a05195",
            "#d45087",
            "#f95d6a",
            "#ff7c43",
            "#ffa600",
        ]
    for color in color_palette:
        if not match(r"^#[0-9A-Fa-f]{6}$", color):
            raise ValueError(f"Invalid hexadecimal color: '{color}'. ")
    return color_palette
