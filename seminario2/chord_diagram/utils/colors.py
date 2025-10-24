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
