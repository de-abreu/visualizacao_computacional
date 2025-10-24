"""
Spectral Ordering for Chord Diagrams

This module provides spectral ordering functionality to arrange nodes in a chord diagram
so that connected nodes with highest weights are placed closer together.
"""

import numpy as np


def spectral_order_matrix(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Apply spectral ordering to a matrix to optimize node arrangement.

    Spectral ordering uses the Fiedler vector (second smallest eigenvector of the
    Laplacian matrix) to find an optimal linear arrangement of nodes that minimizes
    the sum of weighted distances between connected nodes.

    Parameters
    ----------
    matrix : np.ndarray
        A symmetric n x n matrix where matrix[i,j] represents the connection
        strength between nodes i and j. Higher values indicate stronger connections.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        - sorted_matrix: The input matrix reordered according to spectral ordering
        - permutation: The permutation indices that were applied

    Raises
    ------
    ValueError
        If the matrix is not square or symmetric

    Examples
    --------
    >>> import numpy as np
    >>> matrix = np.array([[0, 5, 3], [5, 0, 2], [3, 2, 0]])
    >>> sorted_matrix, permutation = spectral_order_matrix(matrix)
    """

    # Create the Laplacian matrix
    # L = D - W, where D is the degree matrix and W is the weight matrix
    degree_matrix = np.diag(np.sum(matrix, axis=1))
    laplacian = degree_matrix - matrix

    # Compute eigenvectors
    _, eigenvectors = np.linalg.eigh(laplacian)

    # Find the Fiedler vector (second smallest eigenvector, excluding the zero eigenvalue)
    # The smallest eigenvalue is always 0 for connected graphs
    fiedler_vector = eigenvectors[:, 1]

    # Sort nodes by Fiedler vector values
    permutation = np.argsort(fiedler_vector)

    # Apply permutation to reorder the matrix
    sorted_matrix = matrix[np.ix_(permutation, permutation)]

    return sorted_matrix, permutation


def spectral_order(
    matrix: np.ndarray, labels: list[str]
) -> tuple[np.ndarray, list[str]]:
    """
    Apply spectral ordering to a matrix and its corresponding labels.

    Parameters
    ----------
    matrix : np.ndarray
        A symmetric n x n matrix
    labels : list[str]
        List of labels corresponding to matrix rows/columns

    Returns
    -------
    Tuple[np.ndarray, list[str]]
        - sorted_matrix: The reordered matrix
        - sorted_labels: The reordered labels

    Raises
    ------
    ValueError
        If number of labels doesn't match matrix dimensions
    """

    # Spectral ordering is only possible in undirected graphs. So, if the matrix
    # is not symmetrical, give up trying to order it.
    if not np.allclose(matrix, matrix.T):
        return matrix, labels

    sorted_matrix, permutation = spectral_order_matrix(matrix)
    sorted_labels = [labels[i] for i in permutation]

    return sorted_matrix, sorted_labels
