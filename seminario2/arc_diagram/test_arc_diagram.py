"""
Test script for arc_diagram function
"""

import numpy as np
from arc_diagram import arc_diagram


def test_arc_diagram():
    """Test the arc_diagram function with sample data"""

    # Test with sample data
    matrix = np.array([[0, 5, 3], [5, 0, 2], [3, 2, 0]])
    labels = ["A", "B", "C"]

    print("Testing arc_diagram function...")
    print(f"Matrix shape: {matrix.shape}")
    print(f"Matrix:\n{matrix}")
    print(f"Row sums: {np.sum(matrix, axis=1)}")

    # Test the function
    fig = arc_diagram(matrix, labels=labels, title="Test Arc Diagram")
    print(f"Figure created successfully!")
    print(f"Number of traces: {len(fig.data)}")
    fig.show()

    # Check the circle properties
    for i, trace in enumerate(fig.data):
        print(
            f"Circle {i}: {labels[i]}, x={trace.x[0]:.3f}, marker_size={trace.marker.size}"
        )

    # Test with custom color palette
    custom_colors = ["#FF0000", "#00FF00", "#0000FF"]
    fig2 = arc_diagram(
        matrix, labels=labels, color_palette=custom_colors, title="Custom Colors"
    )
    print(f"Custom color figure created successfully!")
    fig2.show()

    # Test with empty matrix
    empty_matrix = np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    fig3 = arc_diagram(empty_matrix, labels=labels)
    print(f"Empty matrix figure created successfully!")
    fig3.show()

    print("All tests passed!")


if __name__ == "__main__":
    test_arc_diagram()
