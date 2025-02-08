import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ClientsideFunction
import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt, timedelta 
import pathlib
from api_routes import api_blueprint

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server
server.register_blueprint(api_blueprint, url_prefix='/api')
hoje = dt.today()
# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

# Read data

dfbr= pd.read_csv(DATA_PATH.joinpath("agendaporangatu.csv"))
#----------------------------------------------------------------------------------

listadeESF=dfbr["Nome da ESF"].unique()
dfbr["Fonte de Admissao"] = dfbr["Fonte de Admissao"].fillna("Não identificado")
listadeAdmissao = dfbr["Fonte de Admissao"].unique().tolist()

#----------------------------------------------------------------------------------
# Date
# Format checkin Time
 # String -> Datetime

dfbr["Hora do Check-In"] = dfbr["Hora do Check-In"].apply(
    lambda x: dt.strptime(x, "%d/%m/%Y %I:%M:%S %p")
) 
#-----------------------------------------------------------------------------------

# Insert weekday and hour of checkin time
# Datetime -> weekday string

dfbr["Dias da semana"] = dfbr["Check-In hora"] = dfbr["Hora do Check-In"]
dfbr["Dias da semana"] = dfbr["Dias da semana"].apply(
    lambda x: dt.strftime(x, "%A")
)  # Datetime -> weekday string

dfbr["Check-In hora"] = dfbr["Check-In hora"].apply(
    lambda x: dt.strftime(x, "%I %p")
) 

day_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_list_pt = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo"]
def diaemingles(dia_em_portugues):
    dias_semana = {
        "segunda": "Monday",
        "terça": "Tuesday",
        "quarta": "Wednesday",
        "quinta": "Thursday",
        "sexta": "Friday",
        "sábado": "Saturday",
        "domingo": "Sunday",
    }
    return dias_semana.get(dia_em_portugues.lower())
#----------------------------------------------------------------------------------------------
checkinduracao = dfbr["Hora do Check-In"].describe()

# Register all departments for callbacks
todosdepartamentos = dfbr["Departamento"].unique().tolist()
wait_time_inputs = [
    Input((i + "_wait_time_graph"), "selectedData") for i in todosdepartamentos
]
score_inputs = [Input((i + "_score_graph"), "selectedData") for i in todosdepartamentos]


def converterparaformato24h(hour_24h):
 
    hour = int(hour_24h.replace('h', ''))
    
    # Determina AM ou PM
    period = "AM" if hour < 12 else "PM"
    
    # Ajusta a hora para o formato de 12h (12 PM é meio-dia e 12 AM é meia-noite)
    hour_12h = hour if hour <= 12 else hour - 12
    if hour == 0:
        hour_12h = 12  # Ajuste para meia-noite
    
    # Retorna o horário formatado
    return f"{hour_12h:02}:00 {period}"




#-----------------------------------------------------------------------------------------------

def cartaodescritor():
    """

    :return: Uma Div contendo a descrição dos gráficos.
    """
    #print('\nEsta função foi chamada -> cartaodescritor \n')
    return html.Div(
        id="cartao-de-descricao",
        children=[
            html.H5("ESFs Porangatu"),
            html.H3("Bem vindo a agenda de postinhos de Porangatu"),
            html.Div(
                id="introducao",
                children="Explore os agendamentos por postinho, por hora e por dia da semana",
            ),
        ],
    )

#------------------------------------------------------------------------------------------------

def gerarcontroledosgraficos():
    """
    :return: Uma Div contendo os controles dos gráficos.
    """
    #print('\nEsta função foi chamada -> gerarcontroledosgraficos \n')
    return html.Div(
        id="control-card",
        children=[
            html.P("Escolha o ESF"),
            dcc.Dropdown(
                id="opcao-ESF",
                options=[{"label": i, "value": i} for i in listadeESF],
                value=listadeESF[0],
            ),
            html.Br(),
            html.P("Selecione a hora de entrada"),
            dcc.DatePickerRange(
                id="selecao-de-data",
                start_date=hoje,  # Data de hoje
                end_date=hoje + timedelta(days=15),
                min_date_allowed=dt(2014, 1, 1),
                max_date_allowed=dt(2025, 12, 31),
                initial_visible_month=hoje,
                display_format="DD/MM/YYYY",
            ),
            html.Br(),
            html.Br(),
            html.P("Escolha a forma de admissão"),
            dcc.Dropdown(
                id="menu-admissao",
                options=[{"label": i, "value": i} for i in listadeAdmissao],
                # value=admit_list[:],
                value=[],
                multi=True,
            ),
            html.Br(),
            # html.Div(
            #     id="reset-btn-outer",
            #     children=html.Button(id="reset-btn", children="Reset", n_clicks=0),
            # ),
        ],
    )

#-------------------------------------------------------------------------------------------------------------------------------------

def gerarmapadecalorpaciente(comeco, fim, ESF, tipoAdmissao):
    """
    :param: comeco: data de inicio da selecao.
    :param: fim: fim da data de selecao.
    :param: ESF: ESF de selecao.
    :param: tipoAdmissao: Tipo de admissão escolhida.

    :return: Mapa de calor por pacientes.
    """
    #print('\nEsta função foi chamada -> gerarmapadecalorpaciente \n')
    filtrado_dfbr = dfbr[(dfbr["Nome da ESF"] == ESF) & (dfbr["Fonte de Admissao"].isin(tipoAdmissao))]
    filtrado_dfbr = filtrado_dfbr.sort_values("Hora do Check-In").set_index("Hora do Check-In")[comeco:fim]
    #print(f'\n\n\n\n\n    O filtrado é {filtrado_dfbr}')

    x_axisbr= ['08h', '09h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h', '18h']
    x_axis = [datetime.time(i).strftime("%I %p") for i in range(8,19)]


    y_axis = day_list

    horadodia = ""
    diadasemana = ""

    # Get z value : sum(number of records) based on x, y,
    z = np.zeros((7, 11))
    annotations = []

    for ind_y, day in enumerate(y_axis):
        dia_filtrado = filtrado_dfbr[filtrado_dfbr["Dias da semana"] == day]
        for ind_x, x_val in enumerate(x_axis):
            sum_of_record = dia_filtrado[dia_filtrado["Check-In hora"] == x_val]["CPF"].sum()
            z[ind_y][ind_x] = sum_of_record
            time_obj=datetime.datetime.strptime(x_val, "%I %p")
            x_val_br=time_obj.strftime("%Hh")
            #print(f' day - {day} day_list_pt {day_list_pt[ind_y]} day_list {day_list[ind_y]} soma de registro - {sum_of_record} ')
            annotation_dict = dict(
                showarrow=False,
                text="<b>" + str(sum_of_record) + "<b>",
                x=x_val_br,
                y=day_list_pt[ind_y],
                font=dict(family="sans-serif"),
            )
            annotations.append(annotation_dict)

    # Heatmap
    hovertemplate = "<b> %{y}  %{x} <br><br> %{z} Registros de paciente"

    data = [
        dict(
            x=x_axisbr,
            y=day_list_pt,
            z=z,
            type="heatmap",
            name="",
            hovertemplate=hovertemplate,
            showscale=False,
            colorscale=[[0, "#caf3ff"], [1, "#2c82ff"]],
        )
    ]

    layout = dict(
        margin=dict(l=70, b=40, t=40, r=50),
        modebar={"orientation": "v"},
        font=dict(family="Open Sans"),
        annotations=annotations,
        xaxis=dict(
            side="top",
            ticks="",
            ticklen=2,
            tickfont=dict(family="sans-serif"),
            tickcolor="#ffffff",
        ),
        yaxis=dict(
            side="left", ticks="", tickfont=dict(family="sans-serif"), ticksuffix=" "
        ),
        hovermode="closest",
        showlegend=False,
    )
    return {"data": data, "layout": layout}

#---------------------------------------------------------------------------------------------------------------------

def geradordetabelalinha(id, estilo , col1, col2, col3):
    """ Generate table rows.

    :param id: ID da tabela linha.
    :param estilo: Estilo do CSS da linha.
    :param col1 (dict): Definindo id e filho para primeira coluna.
    :param col2 (dict): Definindo id e filho para segunda coluna.
    :param col3 (dict): Definindo id e filho para terceira coluna.
    """
    #print('\nEsta função foi chamada -> geradordetabelalinha \n')
    return html.Div(
        id=id,
        className="row table-row",
        style=estilo,
        children=[
            html.Div(
                id=col1["id"],
                style={"display": "table", "height": "100%"},
                className="two columns row-department",
                children=col1["children"],
            ),
            html.Div(
                id=col2["id"],
                style={"textAlign": "center", "height": "100%"},
                className="five columns",
                children=col2["children"],
            ),
            html.Div(
                id=col3["id"],
                style={"textAlign": "center", "height": "100%"},
                className="five columns",
                children=col3["children"],
            ),
        ],
    )

#------------------------------------------------------------------------------------------------------------------

def assistentegeradordetabelalinha(departamento):
    """Função auxiliar.

    :param: departamento (string): Nome do departamento.
    :return: nome da tabela.
    """
    #print('\nEsta função foi chamada -> assistentegeradordetabelalinha \n')
    return geradordetabelalinha(
        departamento,
        {},
        {"id": departamento + "_department", "children": html.B(departamento)},
        {
            "id": departamento + "wait_time",
            "children": dcc.Graph(
                id=departamento + "_wait_time_graph",
                style={"height": "100%", "width": "100%"},
                className="wait_time_graph",
                config={
                    "staticPlot": False,
                    "editable": False,
                    "displayModeBar": False,
                },
                figure={
                    "layout": dict(
                        margin=dict(l=0, r=0, b=0, t=0, pad=0),
                        xaxis=dict(
                            showgrid=False,
                            showline=False,
                            showticklabels=False,
                            zeroline=False,
                        ),
                        yaxis=dict(
                            showgrid=False,
                            showline=False,
                            showticklabels=False,
                            zeroline=False,
                        ),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                },
            ),
        },
        {
            "id": departamento + "_patient_score",
            "children": dcc.Graph(
                id=departamento + "_score_graph",
                style={"height": "100%", "width": "100%"},
                className="patient_score_graph",
                config={
                    "staticPlot": False,
                    "editable": False,
                    "displayModeBar": False,
                },
                figure={
                    "layout": dict(
                        margin=dict(l=0, r=0, b=0, t=0, pad=0),
                        xaxis=dict(
                            showgrid=False,
                            showline=False,
                            showticklabels=False,
                            zeroline=False,
                        ),
                        yaxis=dict(
                            showgrid=False,
                            showline=False,
                            showticklabels=False,
                            zeroline=False,
                        ),
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                    )
                },
            ),
        },
    )

#-----------------------------------------------------------------------------------------------

def iniciatabela():
    """
    :return: tabela filha vazia. É iniciado para registrar todos os ID na página de carregamento.
    """
    #print('\nEsta função foi chamada -> iniciatabela \n')
    # header_row
    header = [
        geradordetabelalinha(
            "header",
            {"height": "50px"},
            {"id": "header_department", "children": html.B("Departamento")},
            {"id": "header_wait_time_min", "children": html.B("Tempo de Espera (Min)")},
            {"id": "header_care_score", "children": html.B("Pontuacao de Cuidado")},
        )
    ]

    # department_row
    rows = [assistentegeradordetabelalinha(departmento) for departmento in todosdepartamentos]
    header.extend(rows)
    tabelavazia = header

    return tabelavazia

#-------------------------------------------------------------------------------------------------------

def geradortabelapaciente(listadefiguras, departamentos, tempodeespera, notadoatendimento):
    """
    :param notadoatendimento: plota nota de atendimento [min, max].
    :param tempo de espera:plota a extenção do tempo de expera [min, max].
    :param listadefiguras: Uma lista das figuras da atual métrica de seleção.
    :param departamentos:  lista de departamentos usados na tabela.
    :return: Patient table.
    """
    #print('\nEsta função foi chamada -> geradortabelapaciente \n')
    # header_row
    header = [
        geradordetabelalinha(
            "header",
            {"height": "50px"},
            {"id": "header_department", "children": html.B("Departamento")},
            {"id": "header_wait_time_min", "children": html.B("Tempo de Espera (Min)")},
            {"id": "header_care_score", "children": html.B("Pontuacao de Cuidado")},
        )
    ]

    # department_row
    rows = [assistentegeradordetabelalinha(department) for department in departamentos]
    #print(f'\n   todosdepartamentos -> {todosdepartamentos} \n\n   departamentos -> {departamentos} \n')
    # empty_row
    empty_departments = [item for item in todosdepartamentos if item not in departamentos]
    if not empty_departments:
        empty_departments = [" "]
    empty_rows = [assistentegeradordetabelalinha(department) for department in empty_departments]
    for ind, department in enumerate(departamentos):
        rows[ind].children[1].children.figure = listadefiguras[ind]
        rows[ind].children[2].children.figure = listadefiguras[ind + len(departamentos)]
    for row in empty_rows[1:]:
        row.style = {"display": "none"}

    # convert empty row[0] to axis row
    #print(f'\n   empty rows -> {empty_rows} \n')
    try:
        empty_rows[0].children[0].children = html.B(
            "graph_ax", style={"visibility": "hidden"}
        )

        empty_rows[0].children[1].children.figure["layout"].update(
            dict(margin=dict(t=-70, b=50, l=0, r=0, pad=0))
        )

        empty_rows[0].children[1].children.config["staticPlot"] = False
        empty_rows[0].children[1].children.figure["layout"]["xaxis"].update(
            dict(
                showline=True,
                showticklabels=True,
                tick0=0,
                dtick=20,
                range=tempodeespera,
            )
        )
        empty_rows[0].children[2].children.figure["layout"].update(
            dict(margin=dict(t=-70, b=50, l=0, r=0, pad=0))
        )

        empty_rows[0].children[2].children.figure["layout"]["xaxis"].update(
            dict(showline=True, showticklabels=True, tick0=0, dtick=0.5, range=notadoatendimento)
        )

        header.extend(rows)
        header.extend(empty_rows)
        return header
    except:
        print('deu erro ao criar bolinhas')

#-----------------------------------------------------------------------------------------------------

def criatabeladefiguras(departamento, dfbrfiltrado, categoria, categoriaespectrox, indiceescolhido):
    """Cria figuras.

    :param department: Nome do departamento.
    :param dfbrfiltrado: Dataframe filtrado.
    :param categoria: Definindo a categoria da figura, entre tempo de espera e nota de atendimento.
    :param categoriaespectrox: espectro do eixo x para a figura
    :param indiceescolhido: índice do ponto escolhido.
    :return: Plotly figura do dicionário.
    """
    aggregation = {
        "Tempo de Espera (Min)": "mean",
        "Pontuacao de Cuidado": "mean",
        "Dias da semana": "first",
        "Hora do Check-In": "first",
        "Check-In hora": "first",
    }
    #print('\nEsta função foi chamada -> criatabeladefiguras \n')
    dfbr_por_departamento = dfbrfiltrado[dfbrfiltrado["Departamento"] == departamento].reset_index()
    agrupado = (dfbr_por_departamento.groupby("Nome").agg(aggregation).reset_index())
    listadeIdPaciente = agrupado["Nome"]

    x = agrupado[categoria]
    y = list(departamento for _ in range(len(x)))

    f = lambda x_val: dt.strftime(x_val, "%d/%m/%Y")
    check_in = (
        agrupado["Hora do Check-In"].apply(f)
        + " "
        + agrupado["Dias da semana"]
        + " "
        + agrupado["Check-In hora"].map(str)
    )

    text_wait_time = (
        "Paciente nº : "
        + listadeIdPaciente
        + "<br>Hora do Check-in: "
        + check_in
        + "<br>Tempo de espera: "
        + agrupado["Tempo de Espera (Min)"].round(decimals=1).map(str)
        + " Minutos,  Nota de atendimento : "
        + agrupado["Pontuacao de Cuidado"].round(decimals=1).map(str)
    )

    layout = dict(
        margin=dict(l=0, r=0, b=0, t=0, pad=0),
        hovermode="closest",
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            range=categoriaespectrox,
        ),
        yaxis=dict(
            showgrid=False, showline=False, showticklabels=False, zeroline=False
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    trace = dict(
        x=x,
        y=y,
        mode="markers",
        marker=dict(size=10, line=dict(width=1, color="#ffffff")),
        color="#2c82ff",
        selected=dict(marker=dict(color="#ff6347", opacity=1)),
        unselected=dict(marker=dict(opacity=0.1)),
        selectedpoints=indiceescolhido,
        hoverinfo="text",
        customdata=listadeIdPaciente,
        text=text_wait_time,
    )
    return {"data": [trace], "layout": layout}


app.layout = html.Div(
    id="app-container",
    children=[

        # Left column
        html.Div(
            id="left-column",
            className="four columns",
            children=[cartaodescritor(), gerarcontroledosgraficos()]
            + [
                html.Div(
                    ["initial child"], id="output-clientside", style={"display": "none"}
                )
            ],
        ),
        # Right column
        html.Div(
            id="right-column",
            className="eight columns",
            children=[
                #Botões de dias da semana
                html.Div(
                    id="weekday-buttons",
                    children=[
                        html.Button(dia, id=f"btn-{dia}", n_clicks=0) for dia in day_list_pt
                    ],
                    style={"display": "flex", "gap": "10px", "margin-bottom": "20px"}
                ),
                 # Patient Volume Heatmap
                html.Div(
                    id="patient_volume_card",
                    children=[
                        html.B("Número de pacientes"),
                        html.Hr(),
                        dcc.Graph(id="patient_volume_hm"),
                    ],
                ),
                html.Button("Resetar", id="reset-btn", n_clicks=0),
                # Patient Wait time by Department
                html.Div(
                    id="wait_time_card",
                    children=[
                        html.B("Tempo de espera do paciente e notas de atendimento"),
                        html.Hr(),
                        html.Div(id="wait_time_table", children=iniciatabela()),
                    ],
                ),
            ],
        ),
    ],
)
#-----------------------------------------------------------------------------------------

@app.callback(
        Output("patient_volume_hm", "figure"),
    [
        Input("selecao-de-data", "start_date"),
        Input("selecao-de-data", "end_date"),
        Input("opcao-ESF", "value"),
        Input("menu-admissao", "value"),
        Input('patient_volume_hm', 'clickData'),
        *[Input(f'btn-{dia}', 'n_clicks') for dia in day_list_pt],
        Input('reset-btn', 'n_clicks')
    ]
)

def update_heatmap(start, end, clinic, admit_type, *args):
    start = start + " 00:00:00"
    end = end + " 00:00:00"
    x_axis = [datetime.time(i).strftime("%I %p") for i in range(8,19)]
    filtrado_dfbr = dfbr[(dfbr["Nome da ESF"] == clinic) & (dfbr["Fonte de Admissao"].isin(admit_type))]
    filtrado_dfbr = filtrado_dfbr.sort_values("Hora do Check-In").set_index("Hora do Check-In")[start:end]
    ctx = dash.callback_context  # Contexto para verificar qual Input disparou o callback
    triggered = ctx.triggered[0]['prop_id'] if ctx.triggered else None
    horas = ['08h', '09h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h', '18h']
    print(f"Triggered by: {triggered}")
    print(f"args: {args}")
    annotations=[]
    # Verificar se há um input disparado
    if not triggered:
        return gerarmapadecalorpaciente(start, end, clinic, admit_type)
    elif triggered == 'reset-btn.n_clicks':
        # Resetar o gráfico para o estado inicial
       return gerarmapadecalorpaciente(start, end, clinic, admit_type)
    elif triggered == 'menu-admissao.value':
    # Lógica para quando o menu-admissao for alterado
        print(f"\n\nTá entrando aqui será? ======================= {admit_type} {start} {end} {clinic}???")
        return gerarmapadecalorpaciente(start, end, clinic, admit_type)
    elif "btn-" in triggered:
        # Se um botão de dia da semana for clicado
        print(f' \n\n  triggered {triggered}')
        dia_clicado = triggered.split(".")[0].split("-")[1]
        day_translation = dict(zip(day_list_pt, day_list))
        dia_clicado_ing= day_translation.get(dia_clicado)
        
        dados_filtrados = filtrado_dfbr[(filtrado_dfbr["Dias da semana"] == dia_clicado_ing)] # Filtra os dados para o dia
        #print(f'dados filtradíssimos -> {dados_filtrados}')
        zfinal = [0,0,0,0,0,0,0,0,0,0,0]
        for ind_x, x_val in enumerate(x_axis):
            nomes = dados_filtrados[dados_filtrados["Check-In hora"] == x_val]["CPF"].sum()
            listanomes = dados_filtrados[dados_filtrados["Check-In hora"] == x_val]["Nome"].astype(str).tolist()
            zfinal[ind_x] = nomes
            
            time_obj=datetime.datetime.strptime(x_val, "%I %p")
            x_val_br=time_obj.strftime("%Hh")
            print(f' \n\n  dados_filtrados {dados_filtrados}{type(dados_filtrados)};\n listanomes {listanomes}{type(listanomes)};\n x_val_br {x_val_br};\n')
            annotation_dict = dict(
            showarrow=False,
            text="<br>".join(listanomes),  # Junta os nomes corretamente
            font=dict(family="sans-serif", size=12, color="black"),
            x=x_val_br,  # Garante que está no centro da célula
            y=dia_clicado,  # Mantém a posição correta no eixo Y
            xref="x1",  # Referência correta para o eixo X
            yref="y1",  # Referência correta para o eixo Y
            align="center",  # Centraliza o texto
        )
            annotations.append(annotation_dict)
        #print(f'dados_filtrados  ---------> {dados_filtrados}' )
        zfim=[np.array(zfinal)]
        z = zfim
        x = horas
        y = [dia_clicado]
        titulo = f"Dados para {dia_clicado}"
    elif triggered == 'patient_volume_hm.clickData':
        # Caso tenha clicado no heatmap
        print(f'{args} args {type(args)} <----------------------------------------------> triggered {triggered}')
        dia_clicado = args[0]['points'][0]['y']  # Captura o dia da semana clicado
        day_translation = dict(zip(day_list_pt, day_list))
        dia_clicado_ing= day_translation.get(dia_clicado)
        
        dados_filtrados = filtrado_dfbr[(filtrado_dfbr["Dias da semana"] == dia_clicado_ing)] # Filtra os dados para o dia
        #print(f'dados filtradíssimos -> {dados_filtrados}')
        zfinal = [0,0,0,0,0,0,0,0,0,0,0]
        for ind_x, x_val in enumerate(x_axis):
            nomes = dados_filtrados[dados_filtrados["Check-In hora"] == x_val]["CPF"].sum()
            listanomes = dados_filtrados[dados_filtrados["Check-In hora"] == x_val]["Nome"].astype(str).tolist()
            zfinal[ind_x] = nomes
            
            time_obj=datetime.datetime.strptime(x_val, "%I %p")
            x_val_br=time_obj.strftime("%Hh")
            print(f' \n\n  dados_filtrados {dados_filtrados}{type(dados_filtrados)};\n listanomes {listanomes}{type(listanomes)};\n x_val_br {x_val_br};\n')
            annotation_dict = dict(
            showarrow=False,
            text="<br>".join(listanomes),  # Junta os nomes corretamente
            font=dict(family="sans-serif", size=12, color="black"),
            x=x_val_br,  # Garante que está no centro da célula
            y=dia_clicado,  # Mantém a posição correta no eixo Y
            xref="x1",  # Referência correta para o eixo X
            yref="y1",  # Referência correta para o eixo Y
            align="center",  # Centraliza o texto
        )
            annotations.append(annotation_dict)
        zfim=[np.array(zfinal)]
        z = zfim
        x = horas
        y = [dia_clicado]
        titulo = f"Dados para {dia_clicado}"
        #print(f' \n\n  annotations {annotations}{type(annotations)};\n nomes {nomes}{type(nomes)};\n')
    else:
        return gerarmapadecalorpaciente(start, end, clinic, admit_type)

    # Criação do gráfico
    
    figure = {
       "data": [{
        "z": z,
        "x": x,
        "y": y,
        "type": "heatmap",
        "colorscale": "Blues",
    }],
        "layout": {
            "title": titulo,
            "xaxis": {"title": "Horas", "tickmode": "linear", "dtick": 1},
            "yaxis": {"title": "Dia da Semana"},
            "annotations": annotations,
            "height": "100%",
        }
    }
    return figure

app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("wait_time_table", "children")] + wait_time_inputs + score_inputs,
)


@app.callback(
    Output("wait_time_table", "children"),
    [
        Input("selecao-de-data", "start_date"),
        Input("selecao-de-data", "end_date"),
        Input("opcao-ESF", "value"),
        Input("menu-admissao", "value"),
        Input("patient_volume_hm", "clickData"),
        *[Input(f'btn-{dia}', 'n_clicks') for dia in day_list_pt],
        Input("reset-btn", "n_clicks"),
    ]
    + wait_time_inputs
    + score_inputs,
)


#-------------------------------------------------------------
def update_table(start, end, clinic, admit_type, heatmap_click, *args):
    #print(f'\n  clinic  -> {clinic} \n admit_type  -> {admit_type} \n')
    start = start + " 00:00:00"
    end = end + " 00:00:00"
    x_axis = [datetime.time(i).strftime("%I %p") for i in range(8,19)]
    filtrado_dfbr = dfbr[(dfbr["Nome da ESF"] == clinic) & (dfbr["Fonte de Admissao"].isin(admit_type))]
    filtrado_dfbr = filtrado_dfbr.sort_values("Hora do Check-In").set_index("Hora do Check-In")[start:end]
    ctx = dash.callback_context
    triggered = ctx.triggered[0]['prop_id'] if ctx.triggered else None


    prop_id = ""
    prop_type = ""
    triggered_value = None
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"].split(".")[0]
        prop_type = ctx.triggered[0]["prop_id"].split(".")[1]
        triggered_value = ctx.triggered[0]["value"]

    # filter data
    filtered_dfbr = dfbr[
        (dfbr["Nome da ESF"] == clinic) & (dfbr["Fonte de Admissao"].isin(admit_type))
    ]
    filtered_dfbr = filtered_dfbr.sort_values("Hora do Check-In").set_index("Hora do Check-In")[
        start:end
    ]
    departamentos = filtered_dfbr["Departamento"].unique()
    #print(f"Triggered by: {triggered}")
    #print(f"tipo de heatmap_click: {type(heatmap_click)}\n heatmapclick: {heatmap_click}")
    filtered_dfbr = dfbr[(dfbr["Nome da ESF"] == clinic) & (dfbr["Fonte de Admissao"].isin(admit_type))]
    filtered_dfbr = filtered_dfbr.sort_values("Hora do Check-In").set_index("Hora do Check-In")[start:end]
    dados_filtrados = filtered_dfbr
    departamentos = filtered_dfbr["Departamento"].unique()
    print(f' \n\nFoi em btn triggered ------------->{triggered} tipo triggered{type(triggered)}; prop_type {prop_type} tipo prop_type{type(prop_type)};')
    # Highlight click data's patients in this table
    if heatmap_click is not None and prop_id != "reset-btn":
        dia_clicado = heatmap_click['points'][0]['y']  # Captura o dia da semana clicado
        #print(f"dia_clicado: {dia_clicado}")
        day_translation = dict(zip(day_list_pt, day_list))
        dia_clicado_ing= day_translation.get(dia_clicado)
        dados_filtrados = filtrado_dfbr[(filtrado_dfbr["Dias da semana"] == dia_clicado_ing)] # Filtra os dados para o dia
        departamentos = dados_filtrados["Departamento"].unique()
        print(f"\ndepartamentos: {departamentos} dados_filtrados: {dados_filtrados}")

    if "btn-" in triggered:
        # Se um botão de dia da semana for clicado
        
        dia_clicado = triggered.split(".")[0].split("-")[1]
        day_translation = dict(zip(day_list_pt, day_list))
        dia_clicado_ing= day_translation.get(dia_clicado)

        dados_filtrados = filtrado_dfbr[(filtrado_dfbr["Dias da semana"] == dia_clicado_ing)]  # Filtra os dados para o dia
        departamentos = dados_filtrados["Departamento"].unique()
        
    wait_time_xrange = [
        filtered_dfbr["Tempo de Espera (Min)"].min() - 2,
        filtered_dfbr["Tempo de Espera (Min)"].max() + 2,
    ]
    score_xrange = [
        filtered_dfbr["Pontuacao de Cuidado"].min() - 0.5,
        filtered_dfbr["Pontuacao de Cuidado"].max() + 0.5,
    ]

    figure_list = []

    if prop_type != "selectedData" or (
            prop_type == "selectedData" and triggered_value is None
        ):  # Default condition, all ""

            for departamento in departamentos:
                department_wait_time_figure = criatabeladefiguras(departamento, dados_filtrados, "Tempo de Espera (Min)", wait_time_xrange, "")
                figure_list.append(department_wait_time_figure)

            for departamento in departamentos:
                department_score_figure = criatabeladefiguras(departamento, dados_filtrados, "Pontuacao de Cuidado", score_xrange, "")
                figure_list.append(department_score_figure)
    

    elif prop_type == "selectedData":
        pacienteescolhido = ctx.triggered[0]["value"]["points"][0]["customdata"]
        indiceescolhido = [ctx.triggered[0]["value"]["points"][0]["pointIndex"]]

        # [] turn on un-selection for all other plots, [index] for this department
        for departamento in departamentos:
            wait_selected_index = []
            if prop_id.split("_")[0] == departamento:
                wait_selected_index = indiceescolhido

            department_wait_time_figure = criatabeladefiguras(
                departamento,
                dados_filtrados,
                "Tempo de Espera (Min)",
                wait_time_xrange,
                wait_selected_index,
            )
            figure_list.append(department_wait_time_figure)

        for departamento in departamentos:  
            score_selected_index = []
            if departamento == prop_id.split("_")[0]:
                score_selected_index = indiceescolhido

            department_score_figure = criatabeladefiguras(
                departamento,
                dados_filtrados,
                "Pontuacao de Cuidado",
                score_xrange,
                score_selected_index,
            )
            figure_list.append(department_score_figure)
            
    table = geradortabelapaciente(figure_list, departamentos, wait_time_xrange, score_xrange)
    return table

# Run the server
if __name__ == "__main__":
    app.run_server(debug=True, port=8050, host="0.0.0.0")
