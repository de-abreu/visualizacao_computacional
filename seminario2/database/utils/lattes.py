from csv import DictReader


def lattes_ids(csv_path: str) -> dict[str, int]:
    d: dict[str, int] = {}
    with open(csv_path, "r") as file:
        for row in DictReader(file):
            d[row["nome"]] = int(row["lattes"].rsplit("/", 1)[1])
    return d
