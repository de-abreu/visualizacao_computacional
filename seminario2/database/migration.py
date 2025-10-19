# pyright: reportAny=false
from json import dumps
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from utils import (
    lattes_ids,
    Article,
    Authorship,
    Base,
    Participation,
    Project,
    Researcher,
    parse_role,
    parse_title,
    parse_type,
    parse_year,
    recover_backup,
)

# Load dataset
DATA_PATH = "../data"
LATTES_DICT = lattes_ids(f"{DATA_PATH}/docentes.csv")
results = recover_backup(f"{DATA_PATH}/professores_all.pkl")

# Parse data for migration
article_id = project_id = 1
articles_dict: dict[str, dict[str, int]] = {}
projects_dict: dict[str, dict[str, str | int | None]] = {}
participation_dict: dict[tuple[int, int], str | None] = {}
authorship_set: set[tuple[int, int]] = set()
participation_set: set[tuple[int, int, str]] = set()
researchers: list[Researcher] = []

for name, (articles, projects) in tqdm(results.items()):
    researcher_id = LATTES_DICT[name]
    researchers.append(Researcher(lattes_id=LATTES_DICT[name], name=name))
    for description in articles:
        title = parse_title(description)
        if title not in articles_dict:
            articles_dict[title] = {"id": article_id, "year": parse_year(description)}
            article_id += 1
        authorship_set.add((researcher_id, articles_dict[title]["id"]))
    for project in projects:
        if project.nome not in projects_dict:
            start, _, end = project.data.partition(" - ")
            projects_dict[project.nome] = {
                "id": project_id,
                "start": int(start),
                "end": None if end == "Atual" else int(end),
                "type": parse_type(project.descricao),
            }
            project_id += 1
        participation_dict[  # pyright: ignore [reportArgumentType]
            (researcher_id, projects_dict[project.nome]["id"])
        ] = parse_role(project.descricao, name)
authorship = [
    Authorship(author_id=author_id, article_id=article_id)
    for author_id, article_id in authorship_set
]
participation = [
    Participation(participant_id=participant_id, project_id=project_id, role=role)
    for (participant_id, project_id), role in participation_dict.items()
]

# Create database
engine = create_engine("sqlite:///lattes.db")
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Create session and populate the database
with Session() as session:
    session.add_all(
        [
            *researchers,
            *[Article(title=key, **value) for key, value in articles_dict.items()],
            *[Project(name=key, **value) for key, value in projects_dict.items()],
        ]
    )
    session.commit()
    session.add_all(authorship + participation)
    session.commit()
