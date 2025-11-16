import pathlib
import pandas as pd
from sqlalchemy import create_engine
import pandas as pd

APP_PATH = str(pathlib.Path(__file__).parent.resolve())
DATABASE_PATH = f"{APP_PATH}/../database/lattes.db"
engine = create_engine(f"sqlite:///{DATABASE_PATH}")

def get_data():
    """
    Retorna as tabelas utilizadas para a visualização em linhas
    
    Returns:
        df (pd.DataFrame): dataframe que relaciona pesquisadores com artigos. Possui as colunas: researcher_name, article_title, article_year
        df_counts (pd.DataFrame): criado a partir de df, relaciona pesquisadores com a quantidade de pesquisas por ano. Possui as colunas: researcher_name, year, count_articles
    """
    
    stmt = """
        SELECT 
            researchers.name as researcher_name, 
            articles.title as article_title,
            articles.year as article_year
        FROM ((authorship
            INNER JOIN articles ON authorship.article_id = articles.id)
            INNER JOIN researchers ON authorship.author_id = researchers.lattes_id);
       """
    df = pd.read_sql_query(stmt, engine)  # researcher_name, article_title, article_year
    df_counts = df.groupby(by=["researcher_name", "article_year"], as_index=False).size() ## guarda as contagens de cada professor e artigos por ano (conta quantos artigos a pessoa escreveu por ano)
    df_counts = df_counts.rename(columns={"size":"count_articles",'article_year':'year'}) ## researcher_name, year, count_articles
    return df,df_counts