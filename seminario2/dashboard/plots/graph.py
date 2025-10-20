import pathlib
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt

from sqlalchemy import create_engine

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
DATABASE_PATH = f"{APP_PATH}/../../database/lattes.db"

engine = create_engine(f"sqlite:///{DATABASE_PATH}")
collaborations_query = """
WITH article_collaborations AS (
    SELECT 
        r1.name AS researcher_1,
        r2.name AS researcher_2,
        a.title AS collaboration,
        'artigo' AS type,
        a.year AS start,
        a.year AS end
    FROM authorship au1
    JOIN authorship au2 ON au1.article_id = au2.article_id AND au1.author_id < au2.author_id
    JOIN researchers r1 ON au1.author_id = r1.lattes_id
    JOIN researchers r2 ON au2.author_id = r2.lattes_id
    JOIN articles a ON au1.article_id = a.id
),
project_collaborations AS (
    SELECT 
        r1.name AS researcher_1,
        r2.name AS researcher_2,
        p.name AS collaboration,
        'projeto' AS type,
        p.start AS start,
        CAST(COALESCE(p.end, strftime('%Y', 'now')) AS INTEGER) AS end
    FROM participation p1
    JOIN participation p2 ON p1.project_id = p2.project_id AND p1.participant_id < p2.participant_id
    JOIN researchers r1 ON p1.participant_id = r1.lattes_id
    JOIN researchers r2 ON p2.participant_id = r2.lattes_id
    JOIN projects p ON p1.project_id = p.id
)
SELECT * FROM article_collaborations
UNION ALL
SELECT * FROM project_collaborations
"""

collaborations = pd.read_sql_query(collaborations_query, engine)  # pyright: ignore [reportUnknownMemberType]
collaboration_counts = (
    collaborations.groupby(["researcher_1", "researcher_2"])
    .size()
    .reset_index(name="weight")
)

G = nx.Graph()
G.add_weighted_edges_from(list(collaboration_counts.itertuples(index=False, name=None)))

nx.draw_spring(G, with_labels=True)
plt.show()
nx.draw_circular(G, with_labels=True)
plt.show()
nx.draw_shell(G, with_labels=True)
plt.show()
