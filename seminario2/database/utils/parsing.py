def parse_title(description: str) -> str:
    start_markers, end_marker = (". . ", ".. ", " . ", ". "), "."
    start_pos = -1
    for start_marker in start_markers:
        if (start_pos := description.find(start_marker)) != -1:
            start_pos += len(start_marker)
            break
    end_pos = description.find(end_marker, start_pos)
    return description[start_pos:end_pos]


def parse_year(description: str) -> int:
    start_marker, end_marker = ", ", "."
    start_pos = description.rfind(start_marker) + len(start_marker)
    end_pos = description.find(end_marker, start_pos)
    return int(description[start_pos:end_pos])


def parse_type(description: str) -> str:
    start_marker, end_marker = "Natureza: ", ".\n"
    start_pos = description.rfind(start_marker) + len(start_marker)
    end_pos = description.find(end_marker, start_pos)
    return description[start_pos:end_pos]


def parse_role(description: str, name: str) -> str:
    start_marker, end_markers = name + " - ", (" /", ".")
    start_pos = description.rfind(start_marker)
    if start_pos == -1:
        return "Integrante"
    start_pos += len(start_marker)
    end_pos = -1
    for end_marker in end_markers:
        if (end_pos := description.find(end_marker, start_pos)) != -1:
            break
    return description[start_pos:end_pos]
