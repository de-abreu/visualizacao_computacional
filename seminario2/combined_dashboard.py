import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import numpy as np
from plotly.graph_objects import Figure
import plotly.graph_objects as go

from arc_diagram.utils.arc_diagram import arc_diagram
from arc_diagram.utils.spectral_ordering import spectral_order
from arc_diagram.utils.validation import validate_colors
from line_graph.data import get_data


def create_combined_dashboard(collab_df: pd.DataFrame, df: pd.DataFrame, df_counts: pd.DataFrame):
    """cria um dashboard combinado do dash com diagrama de arcos e grafico de linhas sincronizados em tempo real.

    comportamento:
    - ao clicar em um no no diagrama de arcos, alterna o pesquisador no conjunto selecionado.
    - o grafico de linhas mostra todos os pesquisadores selecionados ao mesmo tempo.
    - selecionar ou desselecionar pesquisadores pelo dropdown do grafico tambem atualiza o diagrama de arcos.
    """

    # prepara dados para o diagrama de arcos (reutiliza logica do collab_dashboard)
    collab_graph = (
        collab_df.groupby(["researcher_1", "researcher_2"]).size().reset_index(name="collaborations")
    )

    labels = sorted(
        set(collab_graph["researcher_1"]).union(set(collab_graph["researcher_2"]))
    )

    researcher_to_index = {name: idx for idx, name in enumerate(labels)}
    n = len(labels)
    matrix = np.zeros((n, n), dtype=int)
    for _, row in collab_graph.iterrows():
        i = researcher_to_index[row["researcher_1"]]
        j = researcher_to_index[row["researcher_2"]]
        matrix[i, j] = matrix[j, i] = row["collaborations"]

    color_palette = validate_colors(None)
    matrix, labels = spectral_order(matrix, labels)

    fig_arc, arc_trace_indexes, dot_trace_indexes = arc_diagram(
        matrix, labels, color_palette, legend_title="Colaborações"
    )

    arc_start, arc_end = arc_trace_indexes
    dot_start, dot_end = dot_trace_indexes
    arc_traces = list(range(arc_start, arc_end + 1))
    dot_traces = list(range(dot_start, dot_end + 1))

    # cria app dash
    app = dash.Dash(__name__)

    # usa layout flex para evitar sobreposicao e permitir rolagem horizontal no diagrama de arcos
    app.layout = html.Div([
        html.H2('Diagrama de Arcos  ←→  Gráfico de Linhas (sincronizados)'),
        dcc.Store(id='selected-researchers', data=[]),
        html.Div([
            html.Div([
                html.H3('Diagrama de Arcos'),
                # mantem o diagrama de arcos rolavel horizontalmente para evitar sobreposicao
                html.Div(
                    dcc.Graph(
                        id='arc-diagram',
                        figure=fig_arc,
                        config={'displayModeBar': True},
                        style={'width': '100%', 'height': '700px'}
                    ),
                    style={
                        'overflowX': 'auto',
                        'padding': '8px',
                        'border': '1px solid #ddd',
                        'borderRadius': '4px',
                        'backgroundColor': '#fff',
                        'height': '720px'
                    }
                ),
                # area para mostrar detalhes do pesquisador clicado
                html.Div(
                    id='hover-info',
                    style={
                        'marginTop': '12px',
                        'padding': '8px',
                        'border': '1px solid #eee',
                        'maxHeight': '300px',
                        'overflowY': 'auto'
                    }
                ),
            ], style={'flex': '1 1 48%', 'minWidth': '400px', 'marginRight': '10px'}),

            html.Div([
                html.H3('Gráfico de Linhas'),
                html.Label('Selecione um ou mais pesquisadores (ou clique no diagrama):'),
                dcc.Dropdown(
                    id='researcher-dropdown',
                    options=[{'label': str(p), 'value': p} for p in sorted(df['researcher_name'].unique())],
                    value=[],
                    multi=True,
                    style={'width': '100%'}
                ),
                dcc.Graph(id='grafico-linhas', style={'width': '100%', 'height': '700px'}),
            ], style={'flex': '1 1 48%', 'minWidth': '420px'}),
        ], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'flex-start'}),
        html.Div(id='debug', style={'display': 'none'})
    ])

    # callback unificada: atualiza o store tanto pelo clique no diagrama quanto pelo dropdown
    @app.callback(
        Output('selected-researchers', 'data'),
        Input('arc-diagram', 'clickData'),
        Input('researcher-dropdown', 'value'),
        State('selected-researchers', 'data')
    )
    def update_store_from_interaction(clickData, dropdown_value, current_selected):
        ctx = dash.callback_context
        if not ctx.triggered:
            return dash.no_update
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        current_selected = current_selected or []
        # se o trigger veio do dropdown, o store passa a refletir exatamente o valor do dropdown
        if trigger_id == 'researcher-dropdown':
            return dropdown_value or []

        # se o trigger veio do diagrama de arcos, alterna o pesquisador clicado no store
        if trigger_id == 'arc-diagram':
            if not clickData:
                return dash.no_update

            pt = clickData['points'][0]
            custom = pt.get('customdata')
            if isinstance(custom, (list, tuple)):
                idx = int(custom[0])
            else:
                idx = int(custom)

            name = None
            if idx is not None and 0 <= idx < len(labels):
                name = labels[idx]
            else:
                name = pt.get('label') or pt.get('text')
            if not name:
                return dash.no_update
            if name in current_selected:
                return [s for s in current_selected if s != name]
            else:
                return current_selected + [name]
        return dash.no_update

    # callback que mantem o dropdown sincronizado com o store
    @app.callback(
        Output('researcher-dropdown', 'value'),
        Input('selected-researchers', 'data')
    )
    def store_to_dropdown(selected):
        return selected or []

    # callback que atualiza o grafico de linhas quando a selecao muda
    @app.callback(
        Output('grafico-linhas', 'figure'),
        Input('selected-researchers', 'data')
    )
    def update_line_graph(selected):
        if not selected:
            return go.Figure().update_layout(
                title={'text': 'Selecione ao menos um pesquisador', 'y': 0.9, 'x': 0.5, 'xanchor': 'center'}
            )
        researchers = selected
        df_show = df_counts[df_counts['researcher_name'].isin(researchers)].copy()

        # reutiliza a construcao do grafico de linhas do dashboard existente
        blob_dic = {}
        position_setter = {}
        for i, (_, row) in enumerate(df_show.iterrows()):
            year = row['year']
            researcher = row['researcher_name']
            position_setter[(researcher, year)] = i
            count = row['count_articles']
            df_sel = df[(df['researcher_name'] == researcher) & (df['article_year'] == year)]
            blob_text = "<br>".join(df_sel['article_title'].tolist()) if not df_sel.empty else "Sem artigos"
            key = (year, count)
            value = (researcher, blob_text)
            if key not in blob_dic:
                blob_dic[key] = [value]
            else:
                blob_dic[key].append(value)

        blob_texts = [''] * len(df_show)
        for key, value in blob_dic.items():
            year, count = key
            researchers_to_set = []
            blob_text = ''
            if len(value) == 1:
                researcher, text = value[0]
                blob_text += text + "<br>"
                researchers_to_set.append(researcher)
            else:
                square_char = chr(9632)
                for researcher, text in value:
                    blob_text += '<b>' + researcher + '  ' + (square_char * (max(1, 20 - len(researcher)))) + '</b>' + "<br>"
                    blob_text += text + "<br><br>"
                    researchers_to_set.append(researcher)
            for researcher in researchers_to_set:
                index = position_setter[(researcher, year)]
                blob_texts[index] = blob_text

        df_show['blob_texts'] = blob_texts
        fig = go.Figure()
        global_opacity = max(0.2, 1 / max(1, len(researchers)))
        minx = 10000
        maxx = 0
        for researcher in researchers:
            sub = df_show[df_show['researcher_name'] == researcher].sort_values('year')
            if sub.empty:
                continue
            hover_texts = sub['blob_texts'].tolist()
            minx = min(minx, min(sub['year']))
            maxx = max(maxx, max(sub['year']))
            fig.add_trace(go.Scatter(
                x=sub['year'],
                y=sub['count_articles'],
                mode='lines+markers',
                name=researcher,
                customdata=hover_texts,
                hovertemplate="<b>%{customdata}</b><extra></extra>",
                opacity=1.0
            ))
        xtick = 1 if abs(maxx - minx) < 25 else 2
        fig.update_layout(
            xaxis=dict(tickmode='linear', dtick=xtick),
            yaxis=dict(tickmode='linear', dtick=1),
            hovermode='closest',
            title={'text': 'Artigos por pesquisador', 'y': 0.9, 'x': 0.5},
            xaxis_title='Ano',
            yaxis_title='Número de Artigos',
            legend_title='pesquisador'
        )
        return fig

    @app.callback(
        Output('hover-info', 'children'),
        Input('arc-diagram', 'clickData')
    )
    def show_researcher_details(clickData):
        # mostra detalhes apenas no clique (sem hover)
        if not clickData:
            return 'Clique em uma bolinha no diagrama para ver colaborações e trabalhos.'

        pt = clickData['points'][0]
        custom = pt.get('customdata')
        if isinstance(custom, (list, tuple)):
            idx = int(custom[0])
        else:
            idx = int(custom)

        name = None
        if idx is not None and 0 <= idx < len(labels):
            name = labels[idx]
        else:
            name = pt.get('label') or pt.get('text')
        if not name:
            return 'Não foi possível identificar o pesquisador.'

        # encontra colaboracoes do pesquisador
        researcher_collabs = collab_df[
            (collab_df['researcher_1'] == name) | (collab_df['researcher_2'] == name)
        ].copy()
        researcher_collabs = researcher_collabs.sort_values('start')

        # total de colaboracoes
        total_collaborations = len(researcher_collabs)

        # lista de artigos do pesquisador
        df_articles = df[(df['researcher_name'] == name)].copy()

        rows = []
        for _, collab in researcher_collabs.iterrows():
            collaborator = collab['researcher_2'] if collab['researcher_1'] == name else collab['researcher_1']
            start = collab.get('start', '')
            end = collab.get('end', '')
            rows.append(html.Tr([
                html.Td(collaborator),
                html.Td(collab.get('collaboration', '')),
                html.Td(collab.get('type', '')),
                html.Td(str(start)),
                html.Td(str(end))
            ]))

        articles_list = [
            html.Li(a) for a in df_articles['article_title'].tolist()
        ] if not df_articles.empty else [html.Li('Sem artigos registrados')]

        return html.Div([
            html.H4(f'Pesquisador: {name}'),
            html.P(f'Total de colaborações: {total_collaborations}'),
            html.H5('Detalhes das Colaborações:'),
            html.Table([
                html.Thead(html.Tr([
                    html.Th('Colaborador', style={'textAlign': 'left'}),
                    html.Th('Título', style={'textAlign': 'left'}),
                    html.Th('Tipo', style={'textAlign': 'left'}),
                    html.Th('Início', style={'textAlign': 'left'}),
                    html.Th('Término', style={'textAlign': 'left'})
                ])),
                html.Tbody(rows)
            ], style={
                'width': '100%',
                'borderCollapse': 'collapse',
                'border': '1px solid #ddd',
                'marginTop': '10px'
            }),
            html.H5('Artigos'),
            html.Ul(articles_list)
        ], style={'padding': '6px'})

    # callback que atualiza o diagrama de arcos para destacar pesquisadores selecionados
    @app.callback(
        Output('arc-diagram', 'figure'),
        Input('selected-researchers', 'data')
    )
    def update_arc_on_selection(selected):
        selected = selected or []
        updated = Figure(fig_arc)

        # constroi conjunto de indices selecionados
        sel_indices = set()
        label_to_idx = {lbl: i for i, lbl in enumerate(labels)}
        for s in selected:
            if s in label_to_idx:
                sel_indices.add(label_to_idx[s])

        # constroi conjunto de vizinhos: nos diretamente conectados a qualquer pesquisador selecionado
        neighbors = set()
        if sel_indices:
            for si in sel_indices:
                connected_row = matrix[si]
                for j, val in enumerate(connected_row):
                    if val and j != si:
                        neighbors.add(j)

        # atualiza opacidade dos nos: selecionados, vizinhos e demais
        for trace_idx in dot_traces:
            trace = updated.data[trace_idx]
            dot_index = int(trace.customdata[0])
            if dot_index in sel_indices:
                trace.marker.opacity = 1.0
            elif dot_index in neighbors and sel_indices:
                trace.marker.opacity = 0.65
            else:
                trace.marker.opacity = 0.1 if sel_indices else 1.0

        # atualiza opacidade das arestas conforme selecao
        for trace_idx in arc_traces:
            trace = updated.data[trace_idx]
            connected = trace.customdata[0]
            opacity = 1.0 if any(idx in sel_indices for idx in connected) else (0.1 if sel_indices else 1.0)
            color = trace.line.color
            # tenta preservar rgb e apenas ajustar alpha
            if isinstance(color, str) and color.startswith('rgb'):
                rgb_values = color[color.find('(') + 1:color.find(')')].split(',')[:3]
                trace.line.color = f'rgba({rgb_values[0]},{rgb_values[1]},{rgb_values[2]},{opacity})'
            else:
                trace.line.color = trace.line.color

        return updated

    return app


if __name__ == '__main__':
    # runner simples para conveniencia (assume execucao a partir da raiz do repositorio e banco disponivel)
    df, df_counts = get_data()

    # carrega colabores do banco (usuario pode substituir por seu proprio dataframe)
    import sqlite3
    conn = sqlite3.connect('database/lattes.db')
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
    collaborations = pd.read_sql_query(collaborations_query, conn)
    app = create_combined_dashboard(collaborations, df, df_counts)
    app.run(host='127.0.0.1', port=8060)
