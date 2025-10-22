## abreu: filtrar por ano, botoes pra incluir projetos e artigos 
## qual prof colaborou com qual outro, quantas colaborações no total, e dá pra filtrar por ano e no que.

## grafico de linhas que é possível ver vários researcher

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



## ------------------- visualicação

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Histórico de produções científicas por pesquisador"),

    html.Label("Selecione um ou mais pesquisador:"),
    dcc.Dropdown(
        id='researcher-dropdown',
        options=[{'label': p, 'value': p} for p in sorted(df['researcher_name'].unique())],
        value=[],  # valor inicial
        multi=True,     # permite múltiplas seleções
        placeholder="Escolha os pesquisadores..."
    ),

    dcc.Graph(id='grafico-linhas')
])

@app.callback(
    Output('grafico-linhas', 'figure'),
    Input('researcher-dropdown', 'value')
)
def atualizar_grafico_linhas(researchers):
    if not researchers:
        # caso o usuário deselecione todos
        return px.line(title="Selecione pelo menos um researcher.")
    
    df_selected = df[df['researcher_name'].isin(researchers)] ## pega os researcher que o carinha selecionou
    
    ## faz o gráfico de linha
    fig = px.line(
        df_selected,
        x='article_year', y='article_title',
        color='researcher_name',
        markers=True,
        title=f"Artigos publicados por {', '.join(researchers)}"
    )
    fig.update_layout(legend_title="researcher", hovermode='x unified')
    return fig

if __name__ == '__main__':
    app.run(debug=True)
