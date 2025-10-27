
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from pandas import DataFrame

def create_visualization(df:DataFrame,df_counts:DataFrame):
    """
    Cria a visualização de linhas 
    
    Args:
        df (pd.DataFrame): dataframe que relaciona pesquisadores com artigos. Possui as colunas: researcher_name, article_title, article_year
        df_counts (pd.DataFrame): criado a partir de df, relaciona pesquisadores com a quantidade de pesquisas por ano. Possui as colunas: researcher_name, year, count_articles
    
    Returns: 
        app: objeto Dash para rodar a visualização
    """
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
            return go.Figure().update_layout(
                    title={
                        'text': "Selecione pelo menos um pesquisador",
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top',
                        'font':dict(
                            family='Arial',
                            size=24,
                        )
                    }
                )
        
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
                square_char = chr(9632)
                for researcher,text in value:
                    blob_text += '<b>' + researcher + '  ' +(square_char*(100-len(researcher)))+'</b>'+"<br>"
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
        
        minx=10000
        maxx=0
        for researcher in researchers:
            sub = df_show[df_show['researcher_name'] == researcher].sort_values('year')
            if sub.empty:
                continue
            hover_texts = sub['blob_texts'].tolist()
            
            minx = min(minx,min(sub['year']))
            maxx = max(maxx,max(sub['year']))
            
            fig.add_trace(go.Scatter(
                x=sub['year'],
                y=sub['count_articles'],
                mode='lines+markers',
                name=researcher,
                customdata=hover_texts,
                hovertemplate="<b>%{customdata}</b><extra></extra>",
                opacity=global_opacity
            ))
        
        ## caso o range de x seja maior que 25 anos, ele coloca o xtick como 2
        xtick = 1 if abs(maxx-minx)<25 else 2
        
        fig.update_layout(
            xaxis = dict(tickmode = 'linear',dtick = xtick),
            yaxis = dict(tickmode = 'linear',dtick = 1),
            hovermode='closest',    
            title={
                    'text': "Artigos por pesquisador",
                    'y':0.9,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font':dict(
                        family='Arial',
                        size=24,
                    )
                },
            xaxis_title="Ano",
            yaxis_title="Número de Artigos",
            legend_title="pesquisador"
        )
        return fig
    return app