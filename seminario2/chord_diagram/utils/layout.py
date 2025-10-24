from plotly.graph_objects import Layout
from .shapes import ShapeStyle


def create_layout(title: str, size: int, shapes: list[ShapeStyle]) -> Layout:
    hide = {
        "showline": False,
        "zeroline": False,
        "showgrid": False,
        "showticklabels": False,
        "title": "",
    }

    return Layout(
        title=title,
        xaxis=hide,
        yaxis=hide,
        showlegend=False,
        width=size,
        height=size,
        margin={"t": 25, "b": 25, "l": 25, "r": 25},
        hovermode="closest",
        shapes=shapes,
    )
