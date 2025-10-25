"""
Arc Diagram Visualization Module

This module provides functionality to create interactive arc diagrams using Plotly.
Arc diagrams visualize entities as circles with radii proportional to their connection sums.
"""

import numpy as np
import numpy.typing as npt
from plotly.graph_objects import Figure, Scatter
from .dots import Dots


def arc_diagram(
    matrix: npt.NDArray[np.floating | np.integer],
    title: str,
    labels: list[str],
    color_palette: list[str],
    legend_title: str,
    margins: int = 60,
    size: int = 600,
) -> Figure:
    row_sums = np.atleast_1d(np.sum(matrix, axis=1, dtype=np.float64))
    n = len(row_sums)

    # If dataset is empty (all row sums are zero) return an empty plot with the
    # "Dataset is empty" message
    fig = Figure()
    hide = {
        "range": [0, 1],
        "showgrid": False,
        "zeroline": False,
        "showticklabels": False,
        "title": "",
    }
    if np.sum(row_sums) == 0:
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

    dots = Dots(row_sums, color_palette, margins)

    # Add arcs connecting related dots
    # Only draw arcs for the upper triangle to avoid duplicates
    for i in range(n):
        for j in range(i + 1, n):
            if matrix[i, j] == 0:
                continue
            # Calculate arc control points for a smooth curve
            x1, x2 = dots.x_positions[i], dots.x_positions[j]
            y = dots.y_position

            # Create a semi-circle arc
            # Semi-circle parameters
            radius = (x2 - x1) / 2  # Half the distance between dots
            center_x = (x1 + x2) / 2  # Center between the two dots
            arc_height = min(radius * 2, 1 - dots.y_position)

            # Generate points along a semi-circle (180 degrees)
            # Start at 0° (left) and go to 180° (right)
            theta = np.linspace(0, np.pi, 30)  # 30 points for smooth semi-circle
            x_points = center_x + radius * np.cos(theta)
            y_points = y + arc_height * np.sin(theta)

            # Calculate line width based on connection strength
            max_connection = np.max(matrix)
            line_width = 1 + (matrix[i, j] / max_connection) * 4  # 1-5px width

            # Calculate color based on connection strength
            color_intensity = matrix[i, j] / max_connection
            color = f"rgba(100, 100, 100, {0.3 + color_intensity * 0.4})"  # Gray with varying opacity

            # Add the arc trace
            _ = fig.add_trace(
                Scatter(
                    x=x_points,
                    y=y_points,
                    mode="lines",
                    line={
                        "width": line_width,
                        "color": color,
                    },
                    hoverinfo="skip",  # Don't show hover for arcs
                    showlegend=False,
                    customdata=[[i, j]],  # Store which dots this arc connects
                )
            )

    # Store matrix data for hover interactions
    # We'll store the matrix as a list of lists in the figure's metadata
    matrix_list = matrix.tolist()

    # Add custom data to each trace for hover interactions
    for i in range(n):
        _ = fig.add_trace(
            Scatter(
                x=[dots.x_positions[i]],
                y=[dots.y_position],
                mode="markers",
                marker={
                    "size": dots.radii[i],
                    "color": dots.colors[i],
                    "line": {"width": 2, "color": "white"},
                },
                name="",  # Empty name to hide from legend
                hovertemplate=f"Total connections: {row_sums[i]:.0f}",
                showlegend=False,  # Hide individual circles from legend
                customdata=[i],  # Store the index for hover interactions
            )
        )

    # Add text labels underneath each dot
    avg_radius = np.mean(dots.radii)
    label_distance = (
        3 * avg_radius / dots.total_width
    )  # Convert to normalized coordinates

    for i in range(n):
        _ = fig.add_annotation(
            x=dots.x_positions[i]
            + 0.004,  # Place names under the dots, plus 4% the images width to the right
            y=dots.y_position - label_distance,  # Position below the dot
            text=labels[i],
            showarrow=False,
            xanchor="right",
            yanchor="top",
            textangle=-45,
            font=dict(size=10, color="black"),
        )

    # Update layout with custom JavaScript for hover interactions
    _ = fig.update_layout(
        title=title,
        width=dots.total_width,
        height=size,
        xaxis=hide,
        yaxis=hide,
        plot_bgcolor="white",
        showlegend=True,
        legend=dots.add_legend(fig, legend_title),
    )

    # Add custom JavaScript for hover-based opacity filtering
    _ = fig.update_layout(
        hovermode="closest",
        # Store matrix data in the figure's metadata for JavaScript access
        meta={"matrix": matrix_list, "total_dots": n},
    )

    return fig
