"""
Dash App for Interactive Arc Diagram with Hover-based Opacity Filtering
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objects as go
import numpy as np
import numpy.typing as npt
from .utils.arc_diagram import arc_diagram
from .utils.validation import validate_matrix, validate_colors, validate_labels
from .utils.spectral_ordering import spectral_order


def create_arc_diagram_dash(
    matrix: npt.NDArray[np.floating | np.integer],
    title: str = "Arc diagram",
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
    fig = arc_diagram(matrix, title, labels, color_palette)

    # Store matrix data for hover interactions
    matrix_list = matrix.tolist()
    n = matrix.shape[0]

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
        Update dot opacity based on hover interactions.
        When hovering over a dot, reduce opacity of unrelated dots to 10%.
        """
        print(f"DEBUG: Hover data received: {hover_data}")  # Debug logging

        # Start with the original figure
        ctx = dash.callback_context

        # If no hover data, return the original figure with full opacity
        if hover_data is None:
            print("DEBUG: No hover data, resetting all dots to full opacity")
            # Reset all dots to full opacity
            updated_fig = go.Figure(fig)
            for i in range(n):
                updated_fig.data[i].marker.opacity = 1.0
            return updated_fig

        # Get the hovered dot index from customdata
        try:
            # customdata is an integer, not a list
            hovered_index = hover_data["points"][0]["customdata"]
            print(f"DEBUG: Hovered index: {hovered_index}")
        except (KeyError, IndexError, TypeError) as e:
            print(f"DEBUG: Error getting customdata: {e}")
            # Reset all dots to full opacity
            updated_fig = go.Figure(fig)
            for i in range(n):
                updated_fig.data[i].marker.opacity = 1.0
            return updated_fig

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
        updated_fig = go.Figure(fig)

        # Update opacity for all main graph traces (first n traces)
        for i in range(n):
            if i == hovered_index:
                # Keep hovered dot at full opacity
                updated_fig.data[i].marker.opacity = 1.0
            elif i in related_indices:
                # Keep related dots at full opacity
                updated_fig.data[i].marker.opacity = 1.0
            else:
                # Reduce unrelated dots to 10% opacity
                updated_fig.data[i].marker.opacity = 0.1

        print(f"DEBUG: Updated opacity for {n} main graph dots")
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


def main():
    """
    Example usage of the Dash arc diagram app.
    Replace this with your actual matrix data.
    """
    # Example matrix (replace with your actual data)
    matrix = np.array(
        [
            [0, 5, 3, 0, 2],
            [5, 0, 2, 1, 0],
            [3, 2, 0, 4, 1],
            [0, 1, 4, 0, 3],
            [2, 0, 1, 3, 0],
        ]
    )

    labels = ["A", "B", "C", "D", "E"]

    # Create and run the Dash app
    app = create_arc_diagram_dash(
        matrix=matrix,
        title="Interactive Arc Diagram with Hover Filtering",
        labels=labels,
        size=800,
    )

    # Run the app
    app.run(debug=True, host="127.0.0.1", port=8050)


if __name__ == "__main__":
    main()
