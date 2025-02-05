from flask import Blueprint, request, jsonify, send_from_directory
import datetime
import os
import pandas as pd
from time import sleep
import json
import pathlib


#from app import assistant_workflow
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()
# Crie um Blueprint para as rotas da API
api_blueprint = Blueprint('api_blueprint', __name__)
arquivo = DATA_PATH.joinpath("agendaporangatufinal.csv")
print (f'arquivo {arquivo}')
def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    else:
        colunas = ["Fonte de Admissao", "Tipo de Admissao", "Inicio do Atendimento", "Pontuacao de Cuidado", "Hora do Check-In", "Nome", "Nome da ESF", "Departamento", "Diagnostico Principal", "Data/Hora de Alta", "Numero do Atendimento", "Status do Atendimento", "Numero de Registros", "Tempo de Espera (Min)"]
        return pd.DataFrame(columns=colunas)

def salvar_dados(df, arquivo):
    df.to_csv(arquivo, index=False)

def incluir_agendamento(arquivo,nome, fonte, inicio, ESF, departamento):
    df = carregar_dados(arquivo)
    novo_agendamento = {
        "Fonte de Admissao": fonte,
        "Tipo de Admissao": "Eletiva",
        "Inicio do Atendimento": inicio,
        "CPF": 1,
        "Pontuacao de Cuidado": '-',
        "Hora do Check-In": inicio,
        "Nome": nome,
        "Nome da ESF": ESF,
        "Departamento": departamento,
        "Diagnostico Principal": '-',
        "Data/Hora de Alta": "-",
        "Status do Atendimento": "Agendado",
        "Tempo de Espera (Min)": "0"
    }
    df = pd.concat([df, pd.DataFrame([novo_agendamento])], ignore_index=True)
    salvar_dados(df, arquivo)
    return f"Agendamento incluído na data {inicio} na {ESF}!"

def cancelar_agendamento(arquivo, nome):
    df = carregar_dados(arquivo)
    df = df[df["Nome"] != nome]
    salvar_dados(df, arquivo)
    return "Agendamento cancelado com sucesso."

def reagendar_atendimento(arquivo, nome, inicio, ESF, departamento):
    df = carregar_dados(arquivo)
    nova_hora = input("Nova Hora do Check-In: ")
    df.loc[df["Nome"] == nome, "Hora do Check-In"] = inicio
    df.loc[df["Nome"] == nome, "Nome da ESF"] = ESF
    df.loc[df["Nome"] == nome, "Departamento"] = departamento
    df.loc[df["Nome"] == nome, "Status do Atendimento"] = "Reagendado"
    salvar_dados(df, arquivo)
    return f"Agendamento reagendado para a data {nova_hora} com sucesso!"
print(incluir_agendamento(arquivo, "Jefferson Peres", "WhatsApp","2025-02-04 2:39:05 PM", "ESF Primavera", "Clínica Geral"))
@api_blueprint.route('/receber_json', methods=['POST'])
def receber_json():
    try:
        # Recebe o JSON da requisição
        data = request.get_json()
        # Extrai os valores do JSON
        intencao=data.get('intencao')
        nome = data.get('nome')
        fonte= "WhatsApp"
        inicio= data.get('inicio')
        ESF= data.get('esf')
        departamento= data.get('departamento')

        if intencao=="agendamento":
            resposta=incluir_agendamento(arquivo, nome, fonte, inicio, ESF, "Clínica Geral")
        elif intencao=="reagendamento":
            resposta=incluir_agendamento(arquivo, nome, fonte, inicio, ESF, "Clínica Geral")
        elif intencao=="cancelamento":
            resposta=cancelar_agendamento(arquivo, nome)

        return jsonify({"retorno": f"{resposta}"}), 200

    except Exception as e:
        return jsonify({"retorno": f"Erro: {str(e)}"}), 500

@api_blueprint.route('/json/horariosdesejados.json', methods=['GET'])
def get_json(filename='horariosdesejados.json'):
    current_directory = os.getcwd()  # Diretório atual
    filename = 'horariosdesejados.json'  # Nome do arquivo
    return send_from_directory(directory=current_directory, path='./horariosdesejados.json')
