import plotly.graph_objects as go

# Define nodes and their positions
nodes = ["Alice", "Bob", "Charlie", "David", "Eve"]
positions = {node: i for i, node in enumerate(nodes)}

# Define edges with additional information for tooltips
edges = [
    ("Alice", "Bob", "met at a conference"),
    ("Alice", "David", "co-authored a paper"),
    ("Bob", "Eve", "childhood friends"),
    ("Charlie", "Eve", "colleagues at work"),
]


# Function to generate SVG path for a semicircle arc
def get_arc_path(start_pos, end_pos, radius, direction=1):
    center = (start_pos + end_pos) / 2
    path = f"M{start_pos},{0} A{radius},{radius} 0 0,{direction} {end_pos},{0}"
    return path


# Generate shapes for the arcs and create a list of hover text
shapes = []
arc_hover_texts = []
for start, end, description in edges:
    start_pos = positions[start]
    end_pos = positions[end]
    radius = abs(end_pos - start_pos) / 2
    direction = 0 if start_pos < end_pos else 1
    path = get_arc_path(start_pos, end_pos, radius, direction)

    shapes.append(
        dict(
            type="path",
            path=path,
            line=dict(color="rgba(0, 0, 0, 0.5)", width=2),
            hovertext=f"{start} and {end}: {description}",
            hoveron="fills",
        )
    )
    arc_hover_texts.append(f"{start} and {end}: {description}")

# Create the figure
fig = go.Figure()

# Add nodes as a scatter plot with tooltips
fig.add_trace(
    go.Scatter(
        x=list(positions.values()),
        y=[0] * len(nodes),
        mode="markers+text",
        marker=dict(size=20, color="skyblue"),
        text=nodes,
        textposition="bottom center",
        hovertemplate="Node: %{text}<extra></extra>",  # Custom tooltip for nodes
    )
)

# Add a transparent scatter trace for arcs to enable tooltips on them
# This is a workaround since hoverinfo on shapes is not fully supported
fig.add_trace(
    go.Scatter(
        x=[(positions[e[0]] + positions[e[1]]) / 2 for e in edges],
        y=[0] * len(edges),  # Set y-position to 0, same as nodes
        mode="markers",
        marker_size=0,  # Invisible markers
        text=arc_hover_texts,
        hoverinfo="text",
    )
)

# Add the arc shapes to the layout
fig.update_layout(
    shapes=shapes,
    title="Interactive Arc Diagram with Plotly",
    xaxis=dict(showgrid=False, zeroline=False, visible=False),
    yaxis=dict(showgrid=False, zeroline=False, visible=False),
)

fig.show()
