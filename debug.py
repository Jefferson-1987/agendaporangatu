import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, ClientsideFunction

import numpy as np
import pandas as pd
import datetime
from datetime import datetime as dt
import pathlib

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)


# Path
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()

# Read data
df = pd.read_csv(DATA_PATH.joinpath("clinical_analytics.csv"))
dfbr= pd.read_csv(DATA_PATH.joinpath("agendaporangatu.csv"))
#----------------------------------------------------------------------------------
clinic_list = df["Clinic Name"].unique()
df["Admit Source"] = df["Admit Source"].fillna("Not Identified")
admit_list = df["Admit Source"].unique().tolist()

listadeESF=dfbr["Nome da ESF"].unique()
dfbr["Fonte de Admissao"] = dfbr["Fonte de Admissao"].fillna("Não identificado")
listadeAdmissao = dfbr["Fonte de Admissao"].unique().tolist()

#----------------------------------------------------------------------------------
# Date
# Format checkin Time
df["Check-In Time"] = df["Check-In Time"].apply(
    lambda x: dt.strptime(x, "%Y-%m-%d %I:%M:%S %p")
)  # String -> Datetime

dfbr["Hora do Check-In"] = dfbr["Hora do Check-In"].apply(
    lambda x: dt.strptime(x, "%d/%m/%Y %H:%M:%S")
) 
#-----------------------------------------------------------------------------------

# Insert weekday and hour of checkin time
df["Days of Wk"] = df["Check-In Hour"] = df["Check-In Time"]
df["Days of Wk"] = df["Days of Wk"].apply(
    lambda x: dt.strftime(x, "%A")
)  # Datetime -> weekday string

df["Check-In Hour"] = df["Check-In Hour"].apply(
    lambda x: dt.strftime(x, "%I %p")
)  # Datetime -> int(hour) + AM/PM

dfbr["Dias da semana"] = dfbr["Check-In hora"] = dfbr["Hora do Check-In"]
dfbr["Dias da semana"] = dfbr["Dias da semana"].apply(
    lambda x: dt.strftime(x, "%A")
)  # Datetime -> weekday string

dfbr["Check-In hora"] = dfbr["Check-In hora"].apply(
    lambda x: dt.strftime(x, "%H")
) 

day_list = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
day_list_pt = ["Segunda","Terça","Quarta","Quinta","Sexta","Sábado","Domingo",]
#----------------------------------------------------------------------------------------------
check_in_duration = df["Check-In Time"].describe()
checkinduracao = dfbr["Hora do Check-In"].describe()

# Register all departments for callbacks

all_departments = df["Department"].unique().tolist()
todosdepartamentos = dfbr["Departamento"].unique().tolist()
# wait_time_inputs = [
#     Input((i + "_wait_time_graph"), "selectedData") for i in all_departments
# ]
# score_inputs = [Input((i + "_score_graph"), "selectedData") for i in all_departments]

#-----------------------------------------------------------------------------------------------
def description_card():
    """

    :return: A Div containing dashboard title & descriptions.
    """
    return html.Div(
        id="description-card",
        children=[
            html.H5("Clinical Analytics"),
            html.H3("Welcome to the Clinical Analytics Dashboard"),
            html.Div(
                id="intro",
                children="Explore clinic patient volume by time of day, waiting time, and care score.",
            ),
        ],
    )

def cartaodescritor():
    """

    :return: Uma Div contendo a descrição dos gráficos.
    """
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



def generate_control_card():
    """
    :return: A Div containing controls for graphs.
    """
    return html.Div(
        id="control-card",
        children=[
            html.P("Select Clinic"),
            dcc.Dropdown(
                id="clinic-select",
                options=[{"label": i, "value": i} for i in clinic_list],
                value=clinic_list[0],
            ),
            html.Br(),
            html.P("Select Check-In Time"),
            dcc.DatePickerRange(
                id="date-picker-select",
                start_date=dt(2014, 1, 1),
                end_date=dt(2014, 1, 15),
                min_date_allowed=dt(2014, 1, 1),
                max_date_allowed=dt(2014, 12, 31),
                initial_visible_month=dt(2014, 1, 1),
            ),
            html.Br(),
            html.Br(),
            html.P("Select Admit Source"),
            dcc.Dropdown(
                id="admit-select",
                options=[{"label": i, "value": i} for i in admit_list],
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


def gerarcontroledosgraficos():
    """
    :return: Uma Div contendo os controles dos gráficos.
    """
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
                start_date=dt(2014, 1, 1),
                end_date=dt(2014, 1, 15),
                min_date_allowed=dt(2014, 1, 1),
                max_date_allowed=dt(2014, 12, 31),
                initial_visible_month=dt(2014, 1, 1),
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


def generate_patient_volume_heatmap(start, end, clinic, admit_type):
    """
    :param: start: start date from selection.
    :param: end: end date from selection.
    :param: clinic: clinic from selection.
    :param: hm_click: clickData from heatmap.
    :param: admit_type: admission type from selection.

    :return: Patient volume annotated heatmap.
    """

    filtered_df = df[(df["Clinic Name"] == clinic) & (df["Admit Source"].isin(admit_type))]
    filtered_df = filtered_df.sort_values("Check-In Time").set_index("Check-In Time")[start:end]

    x_axis = [datetime.time(i).strftime("%I %p") for i in range(24)]  # 24hr time list
    y_axis = day_list

    hour_of_day = ""
    weekday = ""

    # Get z value : sum(number of records) based on x, y,
    z = np.zeros((7, 24))
    annotations = []

    for ind_y, day in enumerate(y_axis):
        filtered_day = filtered_df[filtered_df["Days of Wk"] == day]
        for ind_x, x_val in enumerate(x_axis):
            sum_of_record = filtered_day[filtered_day["Check-In Hour"] == x_val]["Number of Records"].sum()
            z[ind_y][ind_x] = sum_of_record

            annotation_dict = dict(
                showarrow=False,
                text="<b>" + str(sum_of_record) + "<b>",
                x=x_val,
                y=day,
                font=dict(family="sans-serif"),
            )
            annotations.append(annotation_dict)

    # Heatmap
    hovertemplate = "<b> %{y}  %{x} <br><br> %{z} Patient Records"

    data = [
        dict(
            x=x_axis,
            y=y_axis,
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


def gerarmapadecalorpaciente(comeco, fim, ESF, tipoAdmissao):
    """
    :param: comeco: data de inicio da selecao.
    :param: fim: fim da data de selecao.
    :param: ESF: ESF de selecao.
    :param: tipoAdmissao: Tipo de admissão escolhida.

    :return: Mapa de calor por pacientes.
    """

    filtrado_dfbr = dfbr[(dfbr["Nome da ESF"] == ESF) & (dfbr["Fonte de Admissao"].isin(tipoAdmissao))]
    filtrado_dfbr = filtrado_dfbr.sort_values("Hora do Check-In").set_index("Hora do Check-In")[comeco:fim]

    x_axis = [datetime.time(i).strftime("%H") for i in range(24)]  # 24hr time list
    y_axis = day_list

    horadodia = ""
    diadasemana = ""

    # Get z value : sum(number of records) based on x, y,
    z = np.zeros((7, 24))
    annotations = []

    for ind_y, day in enumerate(y_axis):
        dia_filtrado = filtrado_dfbr[filtrado_dfbr["Dias da semana"] == day]
        for ind_x, x_val in enumerate(x_axis):
            sum_of_record = dia_filtrado[dia_filtrado["Check-In hora"] == x_val]["Numero de Registros"].sum()
            z[ind_y][ind_x] = sum_of_record

            annotation_dict = dict(
                showarrow=False,
                text="<b>" + str(sum_of_record) + "<b>",
                x=x_val,
                y=day,
                font=dict(family="sans-serif"),
            )
            annotations.append(annotation_dict)

    # Heatmap
    hovertemplate = "<b> %{y}  %{x} <br><br> %{z} Registros de paciente"

    data = [
        dict(
            x=x_axis,
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






