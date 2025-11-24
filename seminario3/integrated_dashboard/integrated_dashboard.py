"""
Integrated Dashboard for Collaborative Research Visualization

This module provides a unified dashboard that combines:
- Arc diagram for collaboration networks
- Line graph for publication history
- Bidirectional selection between dropdown and arc diagram
"""

from .utils.arc_diagram import arc_diagram
from .utils.spectral_ordering import spectral_order
from .utils.validation import validate_colors
from dash import dcc, html, Input, Output
from plotly.graph_objects import Figure
import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def create_integrated_dashboard(
    collab_df: pd.DataFrame,
    title: str = "Collaborations between researchers",
    legend_title: str = "Collaboration count",
    color_palette: list[str] | None = None,
) -> dash.Dash:
    """
    Create an integrated dashboard with arc diagram and line graph visualizations.

    Parameters
    ----------
    collab_df : pd.DataFrame
        DataFrame containing collaboration data with columns: researcher_1, researcher_2,
        collaboration, type, start, end
    title : str
        Title of the dashboard
    legend_title : str
        Title of the legend for arc diagram
    color_palette : list[str] | None
        Color palette for the diagram. If None, uses default colors.

    Returns
    -------
    dash.Dash
        Integrated Dash application
    """

    # Define categorical color palette for line graph and labels
    categorical_colors = [
        "#1192e8",
        "#fa4d56",
        "#002d9c",
        "#009d9a",
        "#a56eff",
        "#ee538b",
    ]

    # Prepare collaboration data for arc diagram
    collab_data: pd.DataFrame = (
        collab_df.groupby(["researcher_1", "researcher_2"])
        .size()
        .reset_index(name="collaborations")
    )

    # Get all unique researchers
    researchers = sorted(
        set(collab_data["researcher_1"]).union(set(collab_data["researcher_2"]))
    )

    # Prepare article productivity data for the line graph
    article_data = []
    for researcher in researchers:
        filtered_df = collab_df[
            (collab_df["type"] == "artigo")
            & (
                (collab_df["researcher_1"] == researcher)
                | (collab_df["researcher_2"] == researcher)
            )
        ]

        # Map data to article_data with specified columns
        for _, row in filtered_df.iterrows():
            article_data.append(
                {
                    "researcher": researcher,
                    "article": row["collaboration"],
                    "year": row["start"],
                }
            )

    # Convert to DataFrame
    article_df = pd.DataFrame(article_data)

    # Create mapping from researcher name to matrix index
    researcher_to_index = {name: i for i, name in enumerate(researchers)}

    # Create empty square matrix
    n = len(researchers)
    matrix = np.zeros((n, n), dtype=int)

    # Populate matrix with collaboration values
    for _, row in collab_data.iterrows():
        i = researcher_to_index[row["researcher_1"]]
        j = researcher_to_index[row["researcher_2"]]
        matrix[i, j] = matrix[j, i] = row["collaborations"]

    color_palette = validate_colors(color_palette)

    # Sort data for optimal display
    matrix, labels = spectral_order(matrix, researchers)

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
    arc_trace_indexes = list(range(arc_start, arc_end + 1))
    dot_trace_indexes = list(range(dot_start, dot_end + 1))

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
            # Dropdown section
            html.Div(
                [
                    dcc.Dropdown(
                        id="researcher-dropdown",
                        options=researchers,
                        value=[],
                        multi=True,
                        placeholder=f"Selecione até {len(categorical_colors)} pesquisadores",
                    ),
                ],
                style={"marginBottom": "20px"},
            ),
            # Arc Diagram section
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
                    "marginBottom": "20px",
                },
            ),
            # Line Graph section (replaces hover-info)
            html.Div(
                dcc.Graph(id="line-graph", clear_on_unhover=False),
                style={
                    "border": "1px solid #ddd",
                    "borderRadius": "4px",
                    "padding": "10px",
                    "backgroundColor": "#f9f9f9",
                },
            ),
        ],
        style={
            "width": "97vw",
            "padding": "20px",
            "fontFamily": "sans-serif",
        },
    )

    @app.callback(
        Output("arc-diagram", "figure"),
        [Input("researcher-dropdown", "value")],
    )
    def update_arc_diagram(dropdown_selection: list[str]) -> Figure:
        """
        Update arc diagram based on dropdown selection.
        """
        # If no selected researchers, return original figure
        if not dropdown_selection:
            return Figure(original_fig)

        # Find indices of selected researchers
        selected_indices = set(labels.index(r) for r in dropdown_selection)
        # Find all related indices (collaborators of selected researchers)
        related_indices: set[int] = set()
        for i in selected_indices:
            for j in range(n):
                if matrix_list[i][j] > 0:
                    related_indices.add(j)
        selected_indices |= related_indices

        # Create updated figure with modified opacity
        updated_fig = Figure(fig)

        # Update opacity for dots
        for i in dot_trace_indexes:
            trace = updated_fig.data[i]
            dot_index = trace.customdata[0]  # Extract the integer from the tuple

            # Keep selected dots and related dots at full opacity
            trace.marker.opacity = 1.0 if dot_index in selected_indices else 0.1

        # Update opacity for arcs
        for i in arc_trace_indexes:
            trace = updated_fig.data[i]
            connected_dots = trace.customdata[0]  # [i, j] array
            color = trace.line.color
            rgb_values = color[5:-1].split(",")[:3]

            # Check if this arc connects any selected researcher
            arc_has_selected = any(i in connected_dots for i in selected_indices)
            opacity = 1.0 if arc_has_selected else 0.1
            trace.line.color = (
                f"rgba({rgb_values[0]},{rgb_values[1]},{rgb_values[2]},{opacity})"
            )

        # Update x-axis labels to highlight selected researchers
        # Get the color mapping from line graph
        line_fig = update_line_graph(dropdown_selection)
        researcher_colors = {}
        for trace in line_fig.data:
            if trace.name in dropdown_selection:
                researcher_colors[trace.name] = (
                    trace.marker.color
                    if hasattr(trace.marker, "color")
                    else trace.line.color
                )

        # Update x-axis tick labels with colors for selected researchers
        ticktext = []
        for label in labels:
            if label in dropdown_selection and label in researcher_colors:
                # Apply color to selected researcher label
                color = researcher_colors[label]
                ticktext.append(
                    f'<span style="color: {color}; font-weight: bold">{label}</span>'
                )
            else:
                ticktext.append(label)

        updated_fig.update_layout(
            xaxis=dict(
                tickmode="array", tickvals=list(range(len(labels))), ticktext=ticktext
            )
        )

        return updated_fig

    @app.callback(
        Output("line-graph", "figure"), [Input("researcher-dropdown", "value")]
    )
    def update_line_graph(researchers: list[str]):
        """
        Update line graph based on selected researchers.
        """
        if not researchers:
            return go.Figure().update_layout(
                title={
                    "text": "Selecione pelo menos um pesquisador",
                    "y": 0.9,
                    "x": 0.5,
                    "xanchor": "center",
                    "yanchor": "top",
                    "font": dict(
                        family="sans-serif",
                        size=24,
                    ),
                }
            )

        # Create df_show from article_df with researcher, year, and article_count
        df_show = (
            article_df.groupby(["researcher", "year"])
            .size()
            .reset_index(name="article_count")
        )

        # Build hover texts for articles
        blob_dic = {}  # (year,count):[(researcher_name,text)]
        position_setter = {}

        for i, (_, row) in enumerate(df_show.iterrows()):
            year = row["year"]
            researcher = row["researcher"]
            position_setter[(researcher, year)] = i

            count = row["article_count"]
            df_sel = article_df[
                (article_df["researcher"] == researcher) & (article_df["year"] == year)
            ]
            blob_text = (
                "<br>".join(df_sel["article"].tolist())
                if not df_sel.empty
                else "Sem artigos"
            )

            key = (year, count)
            value = (researcher, blob_text)
            if key not in blob_dic:  # No point overlap
                blob_dic[key] = [value]
            else:  # With point overlap
                blob_dic[key].append(value)

        # Reorganize building the texts
        blob_texts = ["potato"] * len(df_show)
        for key, value in blob_dic.items():
            year, count = key
            blob_text = ""
            researchers_to_set = []
            if len(value) == 1:  # Only one researcher (1 point)
                researcher, text = value[0]
                blob_text += text + "<br>"
                researchers_to_set.append(researcher)
            else:  # More than one researcher (overlap)
                square_char = chr(9632)
                for researcher, text in value:
                    blob_text += (
                        "<b>"
                        + researcher
                        + "  "
                        + (square_char * (100 - len(researcher)))
                        + "</b>"
                        + "<br>"
                    )
                    blob_text += text + "<br>" + "<br>"
                    researchers_to_set.append(researcher)

            # For the set positions, set the text value
            for researcher in researchers_to_set:
                index = position_setter[(researcher, year)]
                blob_texts[index] = blob_text

        df_show["blob_texts"] = blob_texts

        # Build figure manually
        line_fig = go.Figure()
        global_opacity = max(
            0.5, 1 / len(labels)
        )  # Avoid zero opacity if many researchers

        minx = 10000
        maxx = 0
        for researcher in researchers:
            sub = df_show[df_show["researcher"] == researcher].sort_values("year")
            if sub.empty:
                continue
            hover_texts = sub["blob_texts"].tolist()

            minx = min(minx, min(sub["year"]))
            maxx = max(maxx, max(sub["year"]))

            line_fig.add_trace(
                go.Scatter(
                    x=sub["year"],
                    y=sub["article_count"],
                    mode="lines+markers",
                    name=researcher,
                    customdata=hover_texts,
                    hovertemplate="<b>%{customdata}</b><extra></extra>",
                    opacity=global_opacity,
                )
            )

        # If x range is more than 25 years, set xtick to 2
        xtick = 1 if abs(maxx - minx) < 25 else 2

        line_fig.update_layout(
            xaxis=dict(tickmode="linear", dtick=xtick),
            yaxis=dict(tickmode="linear", dtick=1),
            hovermode="closest",
            title={
                "text": "Artigos por pesquisador",
                "y": 0.9,
                "x": 0.5,
                "xanchor": "center",
                "yanchor": "top",
                "font": dict(
                    family="Arial",
                    size=24,
                ),
            },
            xaxis_title="Ano",
            yaxis_title="Número de Artigos",
            legend_title="pesquisador",
        )
        return line_fig

    return app
