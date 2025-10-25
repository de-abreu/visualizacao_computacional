import numpy as np
import numpy.typing as npt
from re import match


def validate_matrix(
    matrix: npt.NDArray[np.floating | np.integer],
) -> tuple[int, npt.NDArray[np.float64]]:
    if matrix.ndim != 2:
        raise ValueError("Matrix must have 2 dimensions")
    if np.any(matrix < 0):
        raise ValueError("Matrix must not contain negative values")
    if not np.allclose(matrix, matrix.T):
        raise ValueError("Matrix must be symmetric")
    return matrix.shape[0], np.atleast_1d(np.sum(matrix, axis=1, dtype=np.float64))


def validate_labels(labels: list[str] | None, length: int) -> list[str]:
    if labels is None:
        return [f"Node {i + 1}" for i in range(length)]
    if len(labels) == length:
        return labels
    raise ValueError("Number of labels must match matrix dimensions")


def validate_colors(color_palette: list[str] | None) -> list[str]:
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
