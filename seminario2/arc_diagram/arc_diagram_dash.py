"""
Dash App for Interactive Arc Diagram with Hover-based Opacity Filtering
"""

from .utils.arc_diagram import arc_diagram
from .utils.spectral_ordering import spectral_order
from .utils.validation import validate_matrix, validate_colors, validate_labels
from dash import dcc, html, Input, Output, callback
from plotly.graph_objects import Figure
import dash
import numpy as np
import numpy.typing as npt


def create_arc_diagram_dash(
    matrix: npt.NDArray[np.floating | np.integer],
    title: str = "Arc diagram",
    legend_title="Connections",
    labels: list[str] | None = None,
    color_palette: list[str] | None = None,
) -> dash.Dash:
    """
    Create a Dash app with interactive arc diagram that supports hover-based opacity filtering.

    Parameters
    ----------
    matrix : np.ndarray
        Symmetric matrix for the arc diagram
    title : str
        Title of the diagram
    legend_title: str
        Title of the legend
    labels : list[str]
        Labels for each node
    color_palette : list[str]
        Color palette for the diagram
    size : int
        Size of the diagram

    Returns
    -------
    dash.Dash
        Dash application with interactive arc diagram
    """

    # Validate parameters
    n = validate_matrix(matrix)
    labels = validate_labels(labels, n)
    color_palette = validate_colors(color_palette)

    # Sort data for optimal display
    matrix, labels = spectral_order(matrix, labels)

    # Create the initial arc diagram figure
    fig, arc_trace_indexes, dot_trace_indexes = arc_diagram(
        matrix, title, labels, color_palette, legend_title
    )

    # Store matrix data for hover interactions
    matrix_list = matrix.tolist()
    n = matrix.shape[0]

    # Store the original figure for opacity restoration
    original_fig = Figure(fig)

    # Use pre-computed trace indices from arc_diagram
    arc_start, arc_end = arc_trace_indexes
    dot_start, dot_end = dot_trace_indexes

    # Create lists of trace indices for dots and arcs
    arc_traces = list(range(arc_start, arc_end + 1))
    dot_traces = list(range(dot_start, dot_end + 1))

    print(
        f"DEBUG: Using pre-computed {len(dot_traces)} dot traces (indices {dot_start}-{dot_end}) and {len(arc_traces)} arc traces (indices {arc_start}-{arc_end})"
    )

    # Create the Dash app
    app = dash.Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Graph(id="arc-diagram", figure=fig, config={"displayModeBar": True}),
            html.Div(id="hover-info", style={"marginTop": 20}),
        ]
    )

    @app.callback(Output("arc-diagram", "figure"), Input("arc-diagram", "hoverData"))
    def update_opacity_on_hover(hover_data):
        """
        Update dot and arc opacity based on hover interactions.
        When hovering over a dot, reduce opacity of unrelated dots and arcs to 10%.
        """
        print(f"DEBUG: Hover data received: {hover_data}")  # Debug logging

        # If no hover data, return the original figure with full opacity
        if hover_data is None:
            print("DEBUG: No hover data, resetting all elements to full opacity")
            # Return the original figure (which has the correct initial opacities)
            return Figure(original_fig)

        # Get the hovered dot index from customdata
        try:
            # customdata is an integer, not a list
            hovered_index = hover_data["points"][0]["customdata"]
            print(f"DEBUG: Hovered index: {hovered_index}")
        except (KeyError, IndexError, TypeError) as e:
            print(f"DEBUG: Error getting customdata: {e}")
            # Reset all elements to full opacity by returning the original figure
            return Figure(original_fig)

        # Only process hover events from main graph dots (not legend dots)
        # Main graph dots have customdata, legend dots don't
        if hovered_index >= n:
            print(f"DEBUG: Legend dot hovered (index {hovered_index}), ignoring")
            # This is a legend dot, return original figure
            return fig

        # Find dots related to the hovered dot (non-zero values in the row)
        related_indices = []
        for j in range(n):
            if matrix_list[hovered_index][j] > 0:
                related_indices.append(j)

        print(f"DEBUG: Related indices for dot {hovered_index}: {related_indices}")

        # Create updated figure with modified opacity
        updated_fig = Figure(fig)

        print(
            f"DEBUG: Using pre-computed {len(dot_traces)} dot traces and {len(arc_traces)} arc traces"
        )

        # Update opacity for dots
        for trace_idx in dot_traces:
            trace = updated_fig.data[trace_idx]
            dot_index = trace.customdata[0]  # Extract the integer from the tuple

            # Keep hovered dot and related dots at full opacity
            if dot_index == hovered_index or dot_index in related_indices:
                trace.marker.opacity = 1.0
            else:
                trace.marker.opacity = 0.1

        # Update opacity for arcs
        for trace_idx in arc_traces:
            trace = updated_fig.data[trace_idx]
            connected_dots = trace.customdata[0]  # [i, j] array
            color = trace.line.color
            rgb_values = color[5:-1].split(",")[:3]
            opacity = 1.0 if hovered_index in connected_dots else 0.1
            trace.line.color = (
                f"rgba({rgb_values[0]},{rgb_values[1]},{rgb_values[2]},{opacity})"
            )

        print(
            f"DEBUG: Updated opacity for {len(dot_traces)} dots and {len(arc_traces)} arcs"
        )
        return updated_fig

    @app.callback(Output("hover-info", "children"), Input("arc-diagram", "hoverData"))
    def display_hover_info(hover_data):
        """Display information about the hovered dot."""
        if hover_data is None:
            return "Hover over a dot to see related connections"

        try:
            hovered_index = hover_data["points"][0]["customdata"][0]
            hovered_label = (
                labels[hovered_index] if labels else f"Node {hovered_index + 1}"
            )

            # Count related dots
            related_count = sum(
                1 for j in range(n) if matrix_list[hovered_index][j] > 0
            )

            return html.Div(
                [
                    html.H4(f"Hovering: {hovered_label}"),
                    html.P(f"Connected to {related_count} other nodes"),
                    html.P("Unrelated nodes are faded to 10% opacity"),
                ]
            )
        except (KeyError, IndexError, TypeError):
            return "Hover over a dot to see related connections"

    return app
