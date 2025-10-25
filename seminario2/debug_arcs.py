"""
Debug script to examine arc diagram trace structure
"""

import numpy as np
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from arc_diagram.utils.arc_diagram import arc_diagram

# Create test matrix
matrix = np.array([
    [0, 5, 3, 0, 2],
    [5, 0, 2, 1, 0],
    [3, 2, 0, 4, 1],
    [0, 1, 4, 0, 3],
    [2, 0, 1, 3, 0],
])

labels = ["A", "B", "C", "D", "E"]

# Create the figure with a default color palette
fig = arc_diagram(matrix, "Test", labels, ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"])

print(f"Total traces: {len(fig.data)}")
print("\nTrace details:")

for i, trace in enumerate(fig.data):
    print(f"\nTrace {i}:")
    print(f"  Type: {trace.type}")
    print(f"  Mode: {getattr(trace, 'mode', 'N/A')}")
    print(f"  Customdata: {getattr(trace, 'customdata', 'N/A')}")
    print(f"  Showlegend: {getattr(trace, 'showlegend', 'N/A')}")

    # Check for marker
    if hasattr(trace, 'marker'):
        print(f"  Has marker: True")
        if hasattr(trace.marker, 'size'):
            print(f"  Marker size: {trace.marker.size}")

    # Check for line
    if hasattr(trace, 'line'):
        print(f"  Has line: True")
        if hasattr(trace.line, 'width'):
            print(f"  Line width: {trace.line.width}")

    # Check if this would be detected as a dot
    if hasattr(trace, 'customdata') and trace.customdata is not None and getattr(trace, 'showlegend', True) == False:
        print(f"  -> Would be detected as MAIN GRAPH DOT")

    # Check if this would be detected as an arc
    elif hasattr(trace, 'line') and getattr(trace, 'mode', None) == 'lines' and hasattr(trace, 'customdata') and trace.customdata is not None:
        print(f"  -> Would be detected as ARC")

    # Check if this would be detected as a legend trace
    elif getattr(trace, 'showlegend', False):
        print(f"  -> Would be detected as LEGEND TRACE")

