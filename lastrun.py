import requests
import csv
from azure.identity import ClientSecretCredential
from azure.identity import InteractiveBrowserCredential
from urllib.parse import urlencode, quote

# Replace this with your required scope
scope = "https://management.azure.com/.default"

# Authenticate interactively via browser
credential = InteractiveBrowserCredential()

subscription_id = 'd5005b6c-0f96-460d-bbe3-39dc6fe24109'
resource_group = 'centric-prd-rg'

# Get an access token
access_token = credential.get_token(scope).token

# Print the access token
print("Access Token:", access_token)

file_path = 'LAs.txt'
# Initialize an empty list to store the values
values_list = []
finalCsv = []
dados = []

# Open the CSV file
with open(file_path, mode='r', newline='') as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)
    
    # Iterate over each row in the CSV file
    for row in csv_reader:
        values_list.extend(row)

    for workflow_name in values_list:
        #print(workflow_name)

        # Endpoint da API
        url = f'https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Logic/workflows/{workflow_name}/runs?api-version=2016-06-01'

        # Cabeçalhos da requisição
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # Fazendo a requisição GET
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            runs = response.json().get('value', [])
            if runs:
                # Obtendo a execução mais recente
                latest_run = runs[0]

                #dados = [
                #    workflow_name,
                #    latest_run['properties']['startTime'],
                #    latest_run['name'],
                #    resource_group
                #]

                print(f"Última Execução: {latest_run['name']}")
                print(f"Status: {latest_run['properties']['status']}")
                print(f"Início: {latest_run['properties']['startTime']}")
                #print(f"Fim: {latest_run['properties']['endTime']}")
            else:
                print("Nenhuma execução encontrada.")

                dados = [
                    workflow_name,
                    'Nenhuma execução encontrada',
                    '',
                    ''
                ]

            finalCsv.append(dados)
        else:
            print(f"Erro na requisição: {response.status_code}, {response.text}")

# Open the CSV file
fileCsvFinal = 'UlimaExecucaoLAs.csv'
with open(fileCsvFinal, mode='a', newline='', encoding='utf-8') as file:
    # Nomes das colunas (chaves do dicionário)
    #campo_nomes = ['Logic App', 'Data Ultima Execucao', 'RunId']
    
    # Criando o objeto DictWriter
    #writer = csv.DictWriter(file, fieldnames=campo_nomes)
    
    # Escreve o cabeçalho
    #writer.writeheader()
    writer = csv.writer(file)
    # Escreve os dados
    writer.writerows(finalCsv)

print(f"Arquivo {fileCsvFinal} criado com sucesso!")