"""
Dash App for Interactive Arc Diagram with Hover-based Opacity Filtering
"""

from .utils.arc_diagram import arc_diagram
from .utils.spectral_ordering import spectral_order
from .utils.validation import validate_matrix, validate_colors, validate_labels
from dash import dcc, html, Input, Output
from plotly.graph_objects import Figure
import dash
import numpy as np
import numpy.typing as npt
import pandas as pd


def create_collab_dashboard(
    collab_df: pd.DataFrame,
    title: str = "Collaborations between researchers",
    legend_title="Collaboration count",
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

    collab_graph: pd.DataFrame = (
        collab_df.groupby(["researcher_1", "researcher_2"])
        .size()
        .reset_index(name="collaborations")
    )

    labels = sorted(
        set(collab_graph["researcher_1"]).union(set(collab_graph["researcher_2"]))
    )

    # Create mapping from researcher name to matrix index directly from the set
    researcher_to_index = {name: idx for idx, name in enumerate(labels)}

    # Create empty square matrix
    n = len(labels)
    matrix = np.zeros((n, n), dtype=int)

    # Populate matrix with collaboration values
    for _, row in collab_graph.iterrows():
        i = researcher_to_index[row["researcher_1"]]
        j = researcher_to_index[row["researcher_2"]]
        matrix[i, j] = matrix[j, i] = row["collaborations"]

    color_palette = validate_colors(color_palette)

    # Sort data for optimal display
    matrix, labels = spectral_order(matrix, labels)

    # Create the initial arc diagram figure
    fig, arc_trace_indexes, dot_trace_indexes = arc_diagram(
        matrix, labels, color_palette, legend_title
    )

    # Store matrix data for hover interactions
    matrix_list = matrix.tolist()

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
            html.H1(
                title,
                style={
                    "textAlign": "left",
                    "marginBottom": "20px",
                },
            ),
            html.Div(
                dcc.Graph(
                    id="arc-diagram", figure=fig, config={"displayModeBar": True}
                ),
                style={
                    "overflowX": "auto",
                    "border": "1px solid #ddd",
                    "borderRadius": "4px",
                    "padding": "10px",
                    "backgroundColor": "#f9f9f9",
                },
            ),
            html.Div(id="hover-info", style={"marginTop": 20}),
        ],
        style={
            "width": "97vw",
            "padding": "20px",
            "fontFamily": "sans-serif",
        },
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
            hovered_index = hover_data["points"][0]["customdata"]
            print(f"DEBUG: Hovered index: {hovered_index}")
        except (KeyError, IndexError, TypeError) as e:
            print(f"DEBUG: Error getting customdata: {e}")
            # Reset all elements to full opacity by returning the original figure
            return Figure(original_fig)

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
        """Display detailed information about the hovered researcher and their collaborations."""
        print(f"DEBUG: Hover data received: {hover_data}")  # Debug logging
        if hover_data is None:
            return "Passe o mouse sobre um ponto para ver as colaborações"

        try:
            hovered_index = hover_data["points"][0]["customdata"]
            print(f"DEBUG: Hovered index: {hovered_index}")
            hovered_label = (
                labels[hovered_index] if labels else f"Node {hovered_index + 1}"
            )

            # Count total collaborations (sum of all connections for this researcher)
            total_collaborations = sum(matrix_list[hovered_index])

            # Get all collaborations for this researcher from the original dataframe
            researcher_collabs = collab_df[
                (collab_df["researcher_1"] == hovered_label)
                | (collab_df["researcher_2"] == hovered_label)
            ].copy()

            # Sort by start date
            researcher_collabs = researcher_collabs.sort_values("start")

            # Create table rows for each collaboration
            table_rows = []
            for _, collab in researcher_collabs.iterrows():
                # Determine the collaborator name (the other researcher)
                collaborator = (
                    collab["researcher_2"]
                    if collab["researcher_1"] == hovered_label
                    else collab["researcher_1"]
                )

                # Translate type to Portuguese
                collab_type = collab["type"]
                start_year = collab["start"]
                end_year = collab["end"] if pd.notna(collab["end"]) else "Presente"

                table_rows.append(
                    html.Tr(
                        [
                            html.Td(collaborator),
                            html.Td(collab["collaboration"]),
                            html.Td(collab_type),
                            html.Td(str(start_year)),
                            html.Td(str(end_year)),
                        ]
                    )
                )

            return html.Div(
                [
                    html.H4(f"Pesquisador: {hovered_label}"),
                    html.P(f"Total de colaborações: {total_collaborations}"),
                    html.H5("Detalhes das Colaborações:"),
                    html.Table(
                        [
                            html.Thead(
                                html.Tr(
                                    [
                                        html.Th("Colaborador"),
                                        html.Th("Título"),
                                        html.Th("Tipo"),
                                        html.Th("Início"),
                                        html.Th("Término"),
                                    ]
                                )
                            ),
                            html.Tbody(table_rows),
                        ],
                        style={
                            "width": "100%",
                            "borderCollapse": "collapse",
                            "border": "1px solid #ddd",
                            "marginTop": "10px",
                        },
                    ),
                ]
            )

        except (KeyError, IndexError, TypeError):
            return "Passe o mouse sobre um ponto para ver as colaborações"

    return app
