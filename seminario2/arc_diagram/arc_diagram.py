"""
Arc Diagram Visualization Module

This module provides functionality to create interactive arc diagrams using Plotly.
Arc diagrams visualize entities as circles with radii proportional to their connection sums.
"""

import numpy as np
import numpy.typing as npt
from plotly.graph_objects import Figure, Scatter
from .utils.validation import validate_matrix, validate_labels, validate_colors
from .utils.dots import Dots


def arc_diagram(
    matrix: npt.NDArray[np.floating | np.integer],
    title: str = "Arc diagram",
    legend_title: str = "Connection ranges",
    labels: list[str] | None = None,
    color_palette: list[str] | None = None,
    size: int = 600,
) -> Figure:
    # Validation
    n, row_sums = validate_matrix(matrix)
    labels = validate_labels(labels, n)
    color_palette = validate_colors(color_palette)

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

    dots = Dots(row_sums, color_palette)

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
                hovertemplate=f"<b>{labels[i]}</b><br>"
                + f"Total connections: {row_sums[i]:.0f}<br>",
                showlegend=False,  # Hide individual circles from legend
            )
        )

    # Update layout
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

    # Update layout using Dots class method

    return fig
