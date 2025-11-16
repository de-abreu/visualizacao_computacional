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


def hex_to_rgba(hex_color: str, opacity: float = 1.0) -> str:
    """
    Convert a hexadecimal color string to rgba format with adjustable opacity.

    Parameters
    ----------
    hex_color : str
        Hexadecimal color string (e.g., "#ff0000", "#f00", "ff0000")
    opacity : float
        Opacity value between 0.0 (transparent) and 1.0 (opaque)

    Returns
    -------
    str
        RGBA color string in format "rgba(r, g, b, a)"

    Raises
    ------
    ValueError
        If hex_color is not a valid hexadecimal color string
        If opacity is not between 0.0 and 1.0

    Examples
    --------
    >>> hex_to_rgba("#ff0000", 0.5)
    'rgba(255, 0, 0, 0.5)'
    >>> hex_to_rgba("#f00", 0.8)
    'rgba(255, 0, 0, 0.8)'
    >>> hex_to_rgba("00ff00", 1.0)
    'rgba(0, 255, 0, 1.0)'
    """

    # Remove '#' if present
    hex_color = hex_color.lstrip("#")

    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return f"rgba({r}, {g}, {b}, {opacity})"
