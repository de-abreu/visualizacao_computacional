import numpy as np
import numpy.typing as npt
from .colors import assign_color
from plotly.graph_objects import Scatter, Figure


class Dots:
    """
    A class to manage the dots (nodes) in an arc diagram.

    This class handles the positioning, sizing, and coloring of nodes
    based on their connection sums.
    """

    def __init__(
        self,
        row_sums: npt.NDArray[np.float64],
        color_palette: list[str],
        margins: int,
        min_radius: int = 10,
        max_radius: int = 30,
    ) -> None:
        """
        Initialize the Dots object.

        Parameters
        ----------
        row_sums : npt.NDArray[np.float64]
            Array containing the sum of connections for each node
        color_palette : list[str]
            Color palette for the nodes
        margins : int
            Margins for the diagram layout
        min_radius : int, optional
            Minimum radius for nodes, by default 10
        max_radius : int, optional
            Maximum radius for nodes, by default 30
        """
        self.values: npt.NDArray[np.float64] = row_sums
        self.color_palette: list[str] = color_palette
        self.count: int = len(self.values)

        # Normalize row sums to get radii between min_radius and max_radius as integers
        self.radii: npt.NDArray[np.int32] = (
            min_radius
            + (self.values - np.min(self.values))
            / (np.max(self.values) - np.min(self.values))
            * (max_radius - min_radius)
        ).astype(np.int32)

        # Centralize dots along the y axis and spread evenly along the x axis
        self.y_position: float = 0.3
        x_positions = []
        current_x = margins

        for i in range(self.count):
            x_positions.append(current_x + self.radii[i])  # Center of circle
            current_x += self.radii[i] * 2

        # Calculate total width and normalize x positions to the [0, 1] range
        self.total_width: int = x_positions[-1] + self.radii[-1] + 2 * margins
        self.x_positions: list[float] = [x / self.total_width for x in x_positions]

        self.colors: list[str] = [
            assign_color(self.values[i], np.max(self.values), color_palette)
            for i in range(self.count)
        ]

    def add_legend(self, fig: Figure, legend_title: str) -> dict[str, str | float]:
        """
        Add a legend to the figure showing color ranges for connection values.

        Parameters
        ----------
        fig : Figure
            Plotly figure to add the legend to
        legend_title : str
            Title for the legend

        Returns
        -------
        dict[str, str | float]
            Legend configuration dictionary for Plotly layout
        """

        # Create color range legend
        # Calculate the connection value ranges for each color in the palette
        num_colors = len(self.color_palette)
        min_connections = np.min(self.values)
        max_connections = np.max(self.values)

        def bounds(i: int):
            lower_bound = (
                min_connections + (max_connections - min_connections) * i / num_colors
            )
            upper_bound = (
                min_connections
                + (max_connections - min_connections) * (i + 1) / num_colors
            )
            return (lower_bound, upper_bound)

        ranges = []
        for i in range(num_colors - 1):
            b = bounds(i)
            ranges.append(f"{b[0]:.0f} - {b[1] - 1:.0f}")
        b = bounds(num_colors - 1)
        ranges.append(f"{b[0]:.0f} - {b[1] - 1:.0f}")

        # Add legend entries for each color range with gradual size progression
        for color, range_text in zip(self.color_palette, ranges):
            _ = fig.add_trace(
                Scatter(
                    x=[None],  # No actual data points - required for legend
                    y=[None],
                    mode="markers",
                    marker={
                        "size": 20,
                        "color": color,
                        "line": {"width": 2, "color": "white"},
                    },
                    name=range_text,
                    showlegend=True,
                )
            )

        return {
            "title": legend_title,
            "x": 0.0,  # Position legend to the left
            "y": 0.7,
            "xanchor": "left",
            "yanchor": "middle",
        }
