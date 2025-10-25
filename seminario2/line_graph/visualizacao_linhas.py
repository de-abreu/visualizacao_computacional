## abreu: filtrar por ano, botoes pra incluir projetos e artigos 
## qual prof colaborou com qual outro, quantas colaborações no total, e dá pra filtrar por ano e no que.

## grafico de linhas que é possível ver vários researcher

import pathlib
import pandas as pd
from sqlalchemy import create_engine
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
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

df = pd.read_sql_query(stmt, engine)  # researcher_name, article_title, article_year

df_counts = df.groupby(by=["researcher_name", "article_year"], as_index=False).size() ## guarda as contagens de cada professor e artigos por ano (conta quantos artigos a pessoa escreveu por ano)
df_counts = df_counts.rename(columns={"size":"count_articles",'article_year':'year'}) ## researcher_name, year, count_articles

## ------------------- visualicação

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("Histórico de produções científicas por pesquisador"),

    html.Label("Selecione um ou mais pesquisadores:"),
    dcc.Dropdown(
        id='researcher-dropdown',
        options=[{'label': p, 'value': p} for p in sorted(df['researcher_name'].unique())],
        value=[],  # valor inicial
        multi=True,     
        placeholder="Escolha os pesquisadores..."
    ),
    
    dcc.Graph(id='grafico-linhas', clear_on_unhover=False),
    html.Div(id='hover-info', style={'whiteSpace': 'pre-line', 'marginTop': '10px', 'border':'1px solid #ddd', 'padding':'8px'})
])

@app.callback(
    Output('grafico-linhas', 'figure'),
    Input('researcher-dropdown', 'value')
)
def atualizar_grafico_linhas(researchers):
    if not researchers:
        return go.Figure().update_layout(title="Selecione pelo menos um pesquisador")
    
    df_show = df_counts[df_counts['researcher_name'].isin(researchers)].copy()
    
    # monta a coluna de textos dos artigos
    blob_dic = {} ## (year,count):[(researcher_name,text)]
    position_setter = {}
    for i,(idx, row) in enumerate(df_show.iterrows()):
        year = row['year']
        researcher = row['researcher_name']
        position_setter[(researcher,year)] = i
        
        count = row['count_articles']
        df_sel = df[(df['researcher_name']==researcher) & (df['article_year']==year)]
        blob_text = "<br>".join(df_sel['article_title'].tolist()) if not df_sel.empty else "Sem artigos"
        
        
        key = (year,count)
        value = (researcher,blob_text)
        if key not in blob_dic: ## sem sobreposição de pontos
            blob_dic[key] = [value]
        else:                     ## com sobreposição de pontos
            blob_dic[key].append(value)
    
    ## retornaniza montnando os textos
    blob_texts = ['potato']*len(df_show)
    for key,value in blob_dic.items():
        year,count = key
        blob_text = ""
        researchers_to_set = []
        if len(value)==1: ## apenas um pesquisador (1 ponto)
            researcher,text = value[0]
            blob_text += text + "<br>"
            researchers_to_set.append(researcher)
        else: ## mais de um pesquisador (sobreposição)
            for researcher,text in value:
                blob_text += researcher + '  ' +('-'*(100-len(researcher)))+"<br>"
                blob_text += text + "<br>"+"<br>"
                researchers_to_set.append(researcher)
        
        ## para as posições do set, sela o valor do text
        for researcher in researchers_to_set:
            index = position_setter[(researcher,year)]
            blob_texts[index] = blob_text
    
    df_show['blob_texts'] = blob_texts
    
    # construindo figura manualmente
    fig = go.Figure()
    global_opacity = max(0.2, 1/len(researchers))  # evita opacidade zero se houver muitos
    
    for researcher in researchers:
        sub = df_show[df_show['researcher_name'] == researcher].sort_values('year')
        if sub.empty:
            continue
        hover_texts = sub['blob_texts'].tolist()
        fig.add_trace(go.Scatter(
            x=sub['year'],
            y=sub['count_articles'],
            mode='lines+markers',
            name=researcher,
            customdata=hover_texts,
            hovertemplate="<b>%{customdata}</b><extra></extra>",
            opacity=global_opacity
        ))
    
    fig.update_layout(
        hovermode='closest',    
        title="Artigos por Professor",
        xaxis_title="Ano",
        yaxis_title="Número de Artigos",
        legend_title="researcher"
    )
    return fig

# @app.callback(
#     Output('hover-info', 'children'),
#     Input('grafico-linhas', 'hoverData'),
#     State('grafico-linhas', 'figure')
# )
# def show_combined_hover(hoverData, fig_state):
#     if not hoverData or not fig_state:
#         return "Passe o mouse sobre um ponto para ver informações."

#     points = hoverData.get('points', [])
#     if not points:
#         return "Passe o mouse sobre um ponto para ver informações."

#     hover_x = points[0]['x']
#     hover_y = points[0]['y']

#     matches = []
#     for trace in fig_state.get('data', []):
#         print("pure tracex: ",trace.get('x', None))
#         xs = trace.get('x', {'_inputArray':[]})['_inputArray']
#         ys = trace.get('y', {'_inputArray':[]})['_inputArray']
        
#         xs = [value for key,value in xs.items() if key.isnumeric()]
#         ys = [value for key,value in ys.items() if key.isnumeric()]
#         print("xs: ",xs)
        
#         customs = trace.get('customdata', [])
#         name = trace.get('name', '')
#         for i, (xv, yv) in enumerate(zip(xs, ys)):
#             # compara X com tolerância para floats
#             print('xv: ',xv,type(xv),'hover_x: ',hover_x,type(hover_x),'yv: ',yv,type(yv),'hover_y: ',hover_y,type(hover_y),)
            
#             xv=int(xv)
#             yv=int(yv)
#             if abs(xv - hover_x) < 1e-6 and abs(yv - hover_y) < 1e-6:
#                 cd = customs[i] if i < len(customs) else None
#                 matches.append((name, cd))

#     if not matches:
#         return "Somente esse ponto (ou sem informações extras)."

#     out_lines = []
#     for name, cd in matches:
#         out_lines.append(f"{name}:\n{cd}")
#         out_lines.append("-"*20)

#     return "\n".join(out_lines)


if __name__ == '__main__':
    app.run(debug=True)