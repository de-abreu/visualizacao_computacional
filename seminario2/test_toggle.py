"""
Test script to debug the toggle behavior issue
"""

import numpy as np
from arc_diagram.arc_diagram_dash import create_arc_diagram_dash

# Create test matrix
matrix = np.array([
    [0, 5, 3, 0, 2],
    [5, 0, 2, 1, 0],
    [3, 2, 0, 4, 1],
    [0, 1, 4, 0, 3],
    [2, 0, 1, 3, 0],
])

labels = ["A", "B", "C", "D", "E"]

# Create the Dash app
app = create_arc_diagram_dash(
    matrix=matrix,
    title="Test Toggle Behavior",
    labels=labels,
)

# Run the app
app.run(debug=True, host="127.0.0.1", port=8052)

