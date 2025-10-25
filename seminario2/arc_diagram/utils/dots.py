import numpy as np
import numpy.typing as npt
from .colors import hex_to_rgba, assign_color
from plotly.graph_objects import Scatter, Figure


class Dots:
    def __init__(
        self,
        row_sums: npt.NDArray[np.float64],
        color_palette: list[str],
        min_radius: int = 10,
        max_radius: int = 30,
    ) -> None:
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
        self.y_position: float = 0.5
        x_positions = []
        current_x = 0

        for i in range(self.count):
            x_positions.append(current_x + self.radii[i])  # Center of circle
            current_x += self.radii[i] * 2

        # Calculate total width and normalize x positions to the [0, 1] range
        self.total_width: int = x_positions[-1] + self.radii[-1]
        self.x_positions: list[float] = [x / self.total_width for x in x_positions]

        self.colors: list[str] = [
            hex_to_rgba(assign_color(self.radii[i], max_radius, color_palette), 0.75)
            for i in range(self.count)
        ]

    def add_legend(self, fig: Figure, legend_title: str) -> dict:
        """Update the figure layout with proper sizing and legend"""
        # Create color range legend
        # Calculate the connection value ranges for each color in the palette
        num_colors = len(self.color_palette)
        min_connections = np.min(self.values)
        max_connections = np.max(self.values)

        # Calculate the connection value ranges and median values for each color
        ranges: list[str] = []
        medians: list[int] = []

        for i in range(num_colors):
            lower_bound = (
                min_connections + (max_connections - min_connections) * i / num_colors
            )
            upper_bound = (
                min_connections
                + (max_connections - min_connections) * (i + 1) / num_colors
            )

            # Calculate median value for this range
            medians.append(round((lower_bound + upper_bound) / 2))
            range_text = f"{lower_bound:.0f} - {upper_bound:.0f}"
            ranges.append(range_text)

        # Calculate radii for median values using the same scaling as main circles
        legend_radii: list[int] = []
        min_radius = self.radii.min()
        max_radius = self.radii.max()
        for median in medians:
            # Scale radius proportionally to median value
            legend_radius = min_radius + (median - min_connections) / (
                max_connections - min_connections
            ) * (max_radius - min_radius)
            legend_radii.append(int(legend_radius))

        # Add legend entries for each color range with proportional sizes
        for color, range_text, legend_radius in zip(
            self.color_palette, ranges, legend_radii
        ):
            fig.add_trace(
                Scatter(
                    x=[None],  # No actual data points - required for legend
                    y=[None],
                    mode="markers",
                    marker={
                        "size": legend_radius,  # Use proportional size based on median value
                        "color": hex_to_rgba(color, 0.75),
                        "line": {"width": 2, "color": "white"},
                    },
                    name=f"Connections: {range_text}",
                    showlegend=True,
                )
            )

        return {
            "title": legend_title,
            "x": 1.02,  # Position legend to the right
            "y": 0.5,
            "xanchor": "left",
            "yanchor": "middle",
        }
