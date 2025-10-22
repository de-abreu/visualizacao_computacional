Como criar a base:
- entra na branch feature/graph-vis  (o feature/database não tá com o bglh)
- instala os requirements.txt
- entra em database/ e roda migration.py
- o SQL está conforme 


import pathlib
import pandas as pd
from sqlalchemy import create_engine
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
DATABASE_PATH = f"{APP_PATH}/../database/lattes.db"
print("DATABASE_PATH: ",DATABASE_PATH)
engine = create_engine(f"sqlite:///{DATABASE_PATH}")

stmt = """
        SELECT 
            researchers.name as researcher_name, 
            articles.title as article_title,
            articles.year as article_year
        FROM ((authorship
            INNER JOIN articles ON authorship.article_id = articles.id)
            INNER JOIN researchers ON authorship.author_id = researchers.lattes_id);
       """

df = pd.read_sql_query(stmt, engine)  # pyright: ignore [reportUnknownMemberType]