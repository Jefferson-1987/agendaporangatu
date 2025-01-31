import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np

# Dados simulados
dias_da_semana = ["Domingo", "Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
horas = list(range(24))

# Criando um DataFrame simulado para o heatmap
np.random.seed(42)
data = pd.DataFrame(
    np.random.randint(0, 5, size=(7, 24)),
    index=dias_da_semana,
    columns=horas
)

# Inicializando o app Dash
app = dash.Dash(__name__)

# Layout do app
app.layout = html.Div([
    html.H1("Heatmap Interativo - Postinhos de Porangatu"),
    html.Div("Clique em um dia da semana para visualizar os dados."),
    html.Div(
        id="weekday-buttons",
        children=[
            html.Button(dia, id=f"btn-{dia}", n_clicks=0) for dia in dias_da_semana
        ],
        style={"display": "flex", "gap": "10px", "margin-bottom": "20px"}
    ),
    dcc.Graph(
        id='heatmap',
        config={'displayModeBar': False},
        style={'height': '60vh'}
    ),
    html.Button("Resetar", id="reset-button", n_clicks=0),
])

# Callback unificado para atualizar o heatmap
@app.callback(
    Output('heatmap', 'figure'),
    [Input(f'btn-{dia}', 'n_clicks') for dia in dias_da_semana] +
    [Input('heatmap', 'clickData'),
     Input('reset-button', 'n_clicks')]
)
def atualizar_heatmap(*args):
    ctx = dash.callback_context  # Contexto para verificar qual Input disparou o callback
    triggered = ctx.triggered[0]['prop_id'] if ctx.triggered else None

    # Verificar se há um input disparado
    if not triggered:
        # Estado inicial do gráfico
        z = data.values
        x = horas
        y = dias_da_semana
        titulo = "Número de pacientes por dia e hora"
    elif triggered == 'reset-button.n_clicks':
        # Resetar o gráfico para o estado inicial
        print(f'\n data -> {data}\n, \n horas -> {horas}\n,\n data.values -> {data.values}\n')  
        z = data.values
        x = horas
        y = dias_da_semana
        titulo = "Número de pacientes por dia e hora"
    elif "btn-" in triggered:
        # Se um botão de dia da semana for clicado
        dia_clicado = triggered.split(".")[0].split("-")[1]
        dados_filtrados = data.loc[[dia_clicado]]  # Filtra os dados para o dia
        print(f'\n dados_filtrados.values[0] -> {dados_filtrados.values[0]}\n,\n dados_filtrados -> {dados_filtrados}\n')
        z = [dados_filtrados.values[0]]
        x = horas
        y = [dia_clicado]
        titulo = f"Dados para {dia_clicado}"
    elif triggered == 'heatmap.clickData':
        # Caso tenha clicado no heatmap
        dia_clicado = args[-2]['points'][0]['y']  # Captura o dia da semana clicado
        dados_filtrados = data.loc[[dia_clicado]]  # Filtra os dados para o dia
        z = [dados_filtrados.values[0]]
        x = horas
        y = [dia_clicado]
        titulo = f"Dados para {dia_clicado}"
        print(f' \n\nFoi em patien_volume_hm x {x}{type(x)}; \n y {y}{type(y)}; z {z}{type(z)};\n')
    else:
        # Default: gráfico inicial
        z = data.values
        x = horas
        y = dias_da_semana
        titulo = "Número de pacientes por dia e hora"

    # Criação do gráfico
    
    figura = {
        "data": [{
            "z": z,
            "x": x,
            "y": y,
            "type": "heatmap",
            "colorscale": "Blues"
        }],
        "layout": {
            "title": titulo,
            "xaxis": {"title": "Horas", "tickmode": "linear", "dtick": 1},
            "yaxis": {"title": "Dia da Semana"},
            "height": 600,
        }
    }
    return figura


# Executando o servidor
if __name__ == '__main__':
    app.run_server(debug=True)




