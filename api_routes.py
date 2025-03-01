from flask import Blueprint, request, jsonify, send_from_directory
import datetime
from google.cloud import bigquery
import os
import pandas as pd
from time import sleep
import json
import pathlib
from dotenv import load_dotenv

client = bigquery.Client()

# define function that uploads a file from the bucket
def enviar_arquivo():
    table_id = "agendaporangatu.dashbigquerypgt.dashporangatu"
    df = pd.read_csv("data/agendaporangatu.csv")

    # Configura a job para sobrescrever a tabela existente
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )
    # Executa o upload para o BigQuery
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    print("Tabela 'dashporangatu' sobrescrita com sucesso! 🚀")

def baixar_arquivo():
    # Executa a consulta para obter todos os dados
    table_id = "agendaporangatu.dashbigquerypgt.dashporangatu"
    query = f"SELECT * FROM `{table_id}`"
    df = client.query(query).to_dataframe()

    # Salva como CSV
    df.to_csv("data/agendaporangatu.csv", index=False, encoding='utf-8')
    print("Tabela exportada como 'agendaporangatu.csv' com sucesso! 🚀")
    return True

def verifica_horario_ocupado(arquivo_csv, horario_procurado):
    # Carrega o arquivo CSV
    df = pd.read_csv(arquivo_csv)

    # Converte a coluna 'Hora do Check-In' para datetime com formato especificado
    df['Hora do Check-In'] = pd.to_datetime(df['Hora do Check-In'], format='%d/%m/%Y %I:%M:%S %p', errors='coerce')

    # Converte o horário procurado para datetime
    horario_procurado = pd.to_datetime(horario_procurado, format='%d/%m/%Y %I:%M:%S %p', errors='coerce')

    # Filtra os registros com o mesmo horário
    registros_mesmo_horario = df[df['Hora do Check-In'] == horario_procurado]

    # Verifica se há mais de 2 usuários ocupando o horário
    if len(registros_mesmo_horario) > 2:
        return 'Este horário está ocupado'
    else:
        return 'Horario disponivel'


baixar_arquivo()
#from app import assistant_workflow
BASE_PATH = pathlib.Path(__file__).parent.resolve()
DATA_PATH = BASE_PATH.joinpath("data").resolve()
# Crie um Blueprint para as rotas da API
api_blueprint = Blueprint('api_blueprint', __name__)

arquivo = DATA_PATH.joinpath("agendaporangatu.csv")
def carregar_dados(arquivo):
    if os.path.exists(arquivo):
        return pd.read_csv(arquivo)
    else:
        colunas = ["Fonte de Admissao", "Tipo de Admissao", "Inicio do Atendimento", "Pontuacao de Cuidado", "Hora do Check-In", "Nome", "Nome da ESF", "Departamento", "Diagnostico Principal", "Data/Hora de Alta", "Numero do Atendimento", "Status do Atendimento", "Numero de Registros", "Tempo de Espera (Min)"]
        return pd.DataFrame(columns=colunas)

def salvar_dados(df, arquivo):
    df.to_csv(arquivo, index=False)

def incluir_agendamento(arquivo,nome, fonte, inicio, ESF, departamento):
    baixar_arquivo()
    df = carregar_dados(arquivo)
    if verifica_horario_ocupado(arquivo, inicio)== 'Horario disponivel':
        novo_agendamento = {
            "Fonte de Admissao": fonte,
            "Tipo de Admissao": "Eletiva",
            "Inicio do Atendimento": inicio,
            "CPF": 1,
            "Pontuacao de Cuidado": '',
            "Hora do Check-In": inicio,
            "Nome": nome,
            "Nome da ESF": ESF,
            "Departamento": departamento,
            "Diagnostico Principal": '',
            "Data/Hora de Alta": "",
            "Status do Atendimento": "Agendado",
            "Tempo de Espera (Min)": "0"
        }
        df = pd.concat([df, pd.DataFrame([novo_agendamento])], ignore_index=True)
        salvar_dados(df, arquivo)
        enviar_arquivo()
        return f"Agendamento incluído na data {inicio} na {ESF}!"
    else:
        return 'Este horário está ocupado'

def cancelar_agendamento(arquivo, nome):
    baixar_arquivo()
    df = carregar_dados(arquivo)
    df = df[df["Nome"] != nome]
    salvar_dados(df, arquivo)
    enviar_arquivo()
    return "Agendamento cancelado com sucesso."

def reagendar_atendimento(arquivo, nome, inicio, ESF, departamento):
    baixar_arquivo()
    df = carregar_dados(arquivo)
    if verifica_horario_ocupado(arquivo, inicio)== 'Horario disponivel':
        nova_hora = f"Nova Hora do Check-In: {inicio}"
        df.loc[df["Nome"] == nome, "Hora do Check-In"] = inicio
        df.loc[df["Nome"] == nome, "Nome da ESF"] = ESF
        df.loc[df["Nome"] == nome, "Departamento"] = departamento
        df.loc[df["Nome"] == nome, "Status do Atendimento"] = "Reagendado"
        salvar_dados(df, arquivo)
        enviar_arquivo()
        return f"Agendamento reagendado para a data {nova_hora} com sucesso!"
    else:
        return 'Este horário está ocupado'


def notaatendimento(arquivo, nome, inicio, nota):
    baixar_arquivo()
    df = carregar_dados(arquivo)
    df.loc[df["Nome"] == nome, "Hora do Check-In"] = inicio
    df.loc[df["Nome"] == nome, "Pontuacao de Cuidado"] = nota
    df.loc[df["Nome"] == nome, "Status do Atendimento"] = "Atendido"
    salvar_dados(df, arquivo)
    enviar_arquivo()
    return f"Sua nota de atendimento {nota} foi enviada com sucesso!"
    
#print(incluir_agendamento(arquivo, "Jefferson Peres", "WhatsApp","25/02/2025 03:00:00 PM", "ESF Vila Primavera", "Clínica Geral"))
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

        if intencao=="agendamento":
            resposta=incluir_agendamento(arquivo, nome, fonte, inicio, ESF, "Clínica Geral")
        elif intencao=="reagendamento":
            resposta=reagendar_atendimento(arquivo, nome, inicio, ESF, "Clínica Geral")
        elif intencao=="cancelamento":
            resposta=cancelar_agendamento(arquivo, nome)
        elif intencao=="notaatendimento":
            nota = data.get('nota')
            resposta=notaatendimento(arquivo, nome, inicio, nota)
            
        return jsonify({"retorno": f"{resposta}"}), 200

    except Exception as e:
        return jsonify({"retorno": f"Erro: {str(e)}"}), 500

@api_blueprint.route('/json/horariosdesejados.json', methods=['GET'])
def get_json(filename='horariosdesejados.json'):
    current_directory = os.getcwd()  # Diretório atual
    filename = 'horariosdesejados.json'  # Nome do arquivo
    return send_from_directory(directory=current_directory, path='./horariosdesejados.json')
