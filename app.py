import dash
from dash import dcc, html, Input, Output, State, dash_table
import pandas as pd
import plotly.express as px

# Autenticação simples
USERNAME = 'admin'
PASSWORD = 'admin'

df_original = pd.read_excel("planilha_dashboard_generica.xlsx")
df_original['RNR'] = pd.to_numeric(df_original['RNR'], errors='coerce')
df_original['MRR'] = pd.to_numeric(df_original['MRR'], errors='coerce')

app = dash.Dash(__name__)
server = app.server  # Para o Render funcionar

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Página de login
login_layout = html.Div(style={'textAlign': 'center', 'padding': '100px'}, children=[
    html.H2("Login do Dashboard"),
    dcc.Input(id='input-username', type='text', placeholder='Usuário', style={'margin': '10px'}),
    dcc.Input(id='input-password', type='password', placeholder='Senha', style={'margin': '10px'}),
    html.Button('Entrar', id='login-button'),
    html.Div(id='login-feedback', style={'color': 'red', 'marginTop': '10px'})
])

# Página do dashboard
dashboard_layout = html.Div(style={'backgroundColor': '#1e1e1e', 'color': '#fff', 'padding': '20px'}, children=[
    html.H1("Painel de Receita por Analista", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Filtrar por Analista:", style={'marginRight': '10px'}),
        dcc.Dropdown(
            id='filtro-analista',
            options=[{'label': nome, 'value': nome} for nome in sorted(df_original['Analista'].unique())],
            placeholder="Selecione o Analista",
            style={'backgroundColor': '#333', 'color': '#000'}
        ),
    ], style={'marginBottom': '30px', 'width': '50%'}),

    html.Div([
        dcc.Graph(id='grafico-rnr', style={'width': '48%', 'display': 'inline-block'}),
        dcc.Graph(id='grafico-mrr', style={'width': '48%', 'display': 'inline-block'}),
    ]),

    html.H3(id='valor-total', style={'textAlign': 'center', 'marginTop': '30px'}),

    html.Div([
        html.H4("Tabela de Dados:", style={'marginTop': '40px'}),
        dash_table.DataTable(
            id='tabela-clientes',
            style_table={'overflowX': 'auto'},
            style_cell={'backgroundColor': '#1e1e1e', 'color': '#fff', 'textAlign': 'left'},
            style_header={'backgroundColor': '#333', 'fontWeight': 'bold'},
        )
    ], style={'marginTop': '30px'}),
])

# Callback da página
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('input-username', 'value'),
    State('input-password', 'value'),
    Input('login-button', 'n_clicks'),
    prevent_initial_call='initial_duplicate'
)
def route_page(pathname, user, pwd, n_clicks):
    if pathname == '/' and user == USERNAME and pwd == PASSWORD:
        return dashboard_layout
    return login_layout

# Callback dos gráficos e tabela
@app.callback(
    Output('grafico-rnr', 'figure'),
    Output('grafico-mrr', 'figure'),
    Output('valor-total', 'children'),
    Output('tabela-clientes', 'data'),
    Output('tabela-clientes', 'columns'),
    Input('filtro-analista', 'value')
)
def atualizar_dashboard(analista):
    dados = df_original[df_original['Analista'] == analista] if analista else df_original.copy()

    fig_rnr = px.bar(dados, x='ID', y='RNR', title='RNR por Cliente')
    fig_mrr = px.bar(dados, x='ID', y='MRR', title='MRR por Cliente')

    for fig in [fig_rnr, fig_mrr]:
        fig.update_layout(paper_bgcolor='#1e1e1e', plot_bgcolor='#1e1e1e', font_color='#fff', xaxis_tickangle=-45)

    total_txt = f"Total RNR: R${dados['RNR'].sum():,.2f} | Total MRR: R${dados['MRR'].sum():,.2f}"
    tabela_dados = dados.to_dict('records')
    tabela_colunas = [{"name": col, "id": col} for col in dados.columns]

    return fig_rnr, fig_mrr, total_txt, tabela_dados, tabela_colunas

if __name__ == '__main__':
    app.run(debug=True)
