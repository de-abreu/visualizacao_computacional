from typing import TypedDict
from plotly.graph_objects import Scatter
from numpy import ndarray


class LineStyle(TypedDict):
    color: str
    width: float


class ShapeStyle(TypedDict):
    line: LineStyle
    path: str
    type: str
    fillcolor: str
    layer: str


def create_shape(path: str, fill_color: str) -> ShapeStyle:
    return {
        "line": {
            "color": "rgb(150,150,150)",
            "width": 0.5,
        },
        "path": path,
        "type": "path",
        "fillcolor": fill_color,
        "layer": "below",
    }


def create_hover(x: ndarray, y: ndarray, text: str, fill_color: str) -> Scatter:
    return Scatter(
        x=x,
        y=y,
        line={"color": fill_color, "shape": "spline", "width": 0.25},
        text=text,
        hoverinfo="text",
        showlegend=False,
    )


def assign_color(
    weight: float | int, max_weight: float | int, color_palette: list[str]
) -> str:
    """
    Assign a color from a palette based on normalized weight.

    Parameters
    ----------
    weight : float | int
        The weight value to normalize
    max_weight : float | int
        The maximum weight value for normalization
    color_palette : list[str]
        List of color strings to choose from

    Returns
    -------
    str
        Color string from the palette

    Notes
    -----
    Normalizes the weight by dividing by max_weight, then multiplies by the
    length of the color palette vector. The result is rounded down to select
    the color at that index. When the normalized weight equals 1, an invalid
    index would be selected (equal to the length of the palette), so we
    return the last valid index instead.
    """
    length = len(color_palette)
    normalized_weight = weight / max_weight
    if normalized_weight == 1:
        return color_palette[-1]
    return color_palette[int(weight / max_weight * (length))]
