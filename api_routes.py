import csv
import os

# Nome do arquivo CSV
ARQUIVO_AGENDA = 'agenda.csv'

# Campos do arquivo CSV
CAMPOS = ['Ordem', 'Nome', 'CPF', 'Horário', 'Dia', 'Especialidade', 'PostoSaude', 'Setor', 'Status']


def inicializar_arquivo():
    """Cria o arquivo CSV se não existir ou atualiza o cabeçalho."""
    if not os.path.exists(ARQUIVO_AGENDA):
        with open(ARQUIVO_AGENDA, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=CAMPOS)
            writer.writeheader()


def calcular_ordem():
    """Calcula a ordem para o próximo agendamento."""
    with open(ARQUIVO_AGENDA, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        linhas = list(reader)
        return f"{len(linhas) + 1}º"


def adicionar_agendamento(nome, cpf, horario, dia, especialidade, posto_saude, setor, status):
    """Adiciona um novo agendamento ao arquivo CSV."""
    ordem = calcular_ordem()  # Calcula a ordem de chegada
    if verificar_conflito(horario, dia, posto_saude):
        print(f"Conflito: Já existe um agendamento no horário {horario} do dia {dia} no posto {posto_saude}.")
        return

    with open(ARQUIVO_AGENDA, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=CAMPOS)
        writer.writerow({
            'Ordem': ordem, 'Nome': nome, 'CPF': cpf, 'Horário': horario, 'Dia': dia,
            'Especialidade': especialidade, 'PostoSaude': posto_saude, 'Setor': setor, 'Status': status
        })
        print(f"Agendamento adicionado com sucesso! Ordem: {ordem}")


def listar_agendamentos():
    """Lista todos os agendamentos."""
    with open(ARQUIVO_AGENDA, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        print("\nAgendamentos:")
        for linha in reader:
            print(linha)


def verificar_conflito(horario, dia, posto_saude):
    """Verifica se já existe um agendamento no mesmo horário, dia e posto."""
    with open(ARQUIVO_AGENDA, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for linha in reader:
            if linha['Horário'] == horario and linha['Dia'] == dia and linha['PostoSaude'] == posto_saude:
                return True
    return False


def filtrar_agendamentos_por_especialidade(especialidade):
    """Filtra agendamentos por especialidade."""
    with open(ARQUIVO_AGENDA, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        print(f"\nAgendamentos para a especialidade: {especialidade}")
        for linha in reader:
            if linha['Especialidade'] == especialidade:
                print(linha)


def filtrar_agendamentos_por_posto(posto_saude):
    """Filtra agendamentos por posto de saúde."""
    with open(ARQUIVO_AGENDA, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        print(f"\nAgendamentos para o posto de saúde: {posto_saude}")
        for linha in reader:
            if linha['PostoSaude'] == posto_saude:
                print(linha)


def remover_agendamento(cpf, horario, dia):
    """Remove um agendamento específico."""
    agendamentos = []
    with open(ARQUIVO_AGENDA, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for linha in reader:
            if not (linha['CPF'] == cpf and linha['Horário'] == horario and linha['Dia'] == dia):
                agendamentos.append(linha)

    with open(ARQUIVO_AGENDA, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=CAMPOS)
        writer.writeheader()
        writer.writerows(agendamentos)

    print("Agendamento removido com sucesso!")


def editar_agendamento(cpf, horario, dia, novos_dados):
    """Edita um agendamento existente."""
    agendamentos = []
    agendamento_encontrado = False
    with open(ARQUIVO_AGENDA, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for linha in reader:
            if linha['CPF'] == cpf and linha['Horário'] == horario and linha['Dia'] == dia:
                novos_dados['Ordem'] = linha['Ordem']  # Mantém a mesma ordem
                agendamentos.append(novos_dados)
                agendamento_encontrado = True
            else:
                agendamentos.append(linha)

    if not agendamento_encontrado:
        print("Agendamento não encontrado.")
        return

    with open(ARQUIVO_AGENDA, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=CAMPOS)
        writer.writeheader()
        writer.writerows(agendamentos)

    print("Agendamento editado com sucesso!")


# Inicialização do sistema
if __name__ == "__main__":
    inicializar_arquivo()

    while True:
        print("\nMenu:")
        print("1. Adicionar agendamento")
        print("2. Listar agendamentos")
        print("3. Filtrar por especialidade")
        print("4. Filtrar por posto de saúde")
        print("5. Remover agendamento")
        print("6. Editar agendamento")
        print("7. Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            nome = input("Digite o nome: ")
            cpf = input("Digite o CPF: ")
            horario = input("Digite o horário (HH:MM): ")
            dia = input("Digite o dia (DD/MM/AAAA): ")
            especialidade = input("Digite a especialidade: ")
            posto_saude = input("Digite o posto de saúde: ")
            setor = input("Digite o setor: ")
            status = input("Digite o status do agendamento (Confirmado/Pendente/Cancelado): ")
            adicionar_agendamento(nome, cpf, horario, dia, especialidade, posto_saude, setor, status)
        elif escolha == '2':
            listar_agendamentos()
        elif escolha == '3':
            especialidade = input("Digite a especialidade para filtrar: ")
            filtrar_agendamentos_por_especialidade(especialidade)
        elif escolha == '4':
            posto_saude = input("Digite o posto de saúde para filtrar: ")
            filtrar_agendamentos_por_posto(posto_saude)
        elif escolha == '5':
            cpf = input("Digite o CPF do agendamento a ser removido: ")
            horario = input("Digite o horário do agendamento: ")
            dia = input("Digite o dia do agendamento: ")
            remover_agendamento(cpf, horario, dia)
        elif escolha == '6':
            cpf = input("Digite o CPF do agendamento a ser editado: ")
            horario = input("Digite o horário do agendamento: ")
            dia = input("Digite o dia do agendamento: ")
            novos_dados = {
                'Nome': input("Digite o novo nome: "),
                'CPF': cpf,
                'Horário': input("Digite o novo horário (HH:MM): "),
                'Dia': input("Digite o novo dia (DD/MM/AAAA): "),
                'Especialidade': input("Digite a nova especialidade: "),
                'PostoSaude': input("Digite o novo posto de saúde: "),
                'Setor': input("Digite o novo setor: "),
                'Status': input("Digite o novo status do agendamento (Confirmado/Pendente/Cancelado): ")
            }
            editar_agendamento(cpf, horario, dia, novos_dados)
        elif escolha == '7':
            print("Saindo...")
            break
        else:
            print("Opção inválida!")
