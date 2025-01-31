import pandas as pd
import random

# Carregar o arquivo CSV
arquivo = "agendaporangatu.csv"
df = pd.read_csv(arquivo)

# Lista de valores para substituição
novos_valores = ["WhatsApp", "Telefone", "Pessoalmente"]

# Substituir aleatoriamente os valores na coluna 'Fonte de Admissao'
df["Fonte de Admissao"] = df["Fonte de Admissao"].apply(lambda x: random.choice(novos_valores))

# Salvar o arquivo modificado
df.to_csv("agendaporangatu_modificado.csv", index=False)

print("Substituição concluída e arquivo salvo como 'agendaporangatu_modificado.csv'")