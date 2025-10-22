import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Dados de exemplo
data = {
    'professor': ['Ana', 'Ana', 'Ana', 'Bruno', 'Bruno', 'Carlos', 'Carlos', 'Daniela', 'Daniela'],
    'ano': [2019, 2020, 2021, 2020, 2021, 2021, 2022, 2020, 2022],
    'artigos': [2, 5, 4, 1, 3, 2, 5, 4, 7]
}
df = pd.DataFrame(data)

# Cria app Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H2("📈 Produção científica por professor"),

    html.Label("Selecione um ou mais professores:"),
    dcc.Dropdown(
        id='professor-dropdown',
        options=[{'label': p, 'value': p} for p in sorted(df['professor'].unique())],
        value=['Ana'],  # valor inicial
        multi=True,     # permite múltiplas seleções
        placeholder="Selecione ao menos um profe"
    ),

    dcc.Graph(id='grafico-linhas')
])

@app.callback(
    Output('grafico-linhas', 'figure'),
    Input('professor-dropdown', 'value')
)
def atualizar_grafico(professores):
    if not professores:
        # caso o usuário deselecione todos
        return px.line(title="Selecione pelo menos um professor.")
    
    dff = df[df['professor'].isin(professores)]
    fig = px.line(
        dff,
        x='ano', y='artigos',
        color='professor',
        markers=True,
        title=f"Artigos publicados por {', '.join(professores)}"
    )
    fig.update_layout(legend_title="Professor", hovermode='x unified')
    return fig

if __name__ == '__main__':
    app.run(debug=True)
