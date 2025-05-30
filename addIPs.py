from azure.identity import DefaultAzureCredential
from azure.mgmt.logic import LogicManagementClient
from azure.identity import InteractiveBrowserCredential
import copy

# Configurações
subscription_id = 'cd53d955-4364-4c85-9159-662daadf6c80'
resource_group = 'centric-qua-rg'
#listagem de LA que deseja inserir novos IPS
listLogicAppName = ['Centric.CreditRisk.UpsertData'] 
# Listagem de IP que quer permitir
listIpCsv = ["4.175.0.0/16", "4.180.0.0/16", "4.210.128.0/17"]  
currentList = []

# Replace this with your required scope
scope = "https://management.azure.com/.default"

# Authenticate interactively via browser
credential = InteractiveBrowserCredential()

# Autenticação
client = LogicManagementClient(credential, subscription_id)

for logic_app_name in listLogicAppName:
    # Pega a definição atual da Logic App
    logic_app = client.workflows.get(resource_group, logic_app_name)
    # Validando se a LA possui restricao de ip habilitada
    if logic_app.access_control:
        definition = logic_app.access_control

        # Copia a definição para alterar
        new_definition = copy.deepcopy(definition)

        trigger = new_definition.triggers
        if trigger.allowed_caller_ip_addresses:
            allowed_ips = trigger.allowed_caller_ip_addresses
            for ip in allowed_ips:
                # Adiciona o IP se ainda não estiver na lista
                if ip.address_range:
                    currentList.append(ip.address_range)
            
            finalList = [item for item in listIpCsv if item not in currentList]
            for ip in finalList:
                newIp = {
                    "additional_properties": {},
                    "address_range": ip
                }
                allowed_ips.append(newIp)

            if finalList:
                # Atualiza a definição da Logic App
                workflow_params = {
                    'location': logic_app.location,
                    'access_control': new_definition,
                    'definition': logic_app.definition,
                    'tags': logic_app.tags
                }

                if logic_app.parameters:
                    workflow_params = {
                        'location': logic_app.location,
                        'access_control': new_definition,
                        'definition': logic_app.definition,
                        'parameters': logic_app.parameters,
                        'tags': logic_app.tags
                    }

                # Faz a atualização (replace)
                client.workflows.create_or_update(resource_group, logic_app_name, workflow_params)

                print(f"IP {finalList} adicionado em Logic App {logic_app_name}")
            else:
                print(f"Nenhum IP foi adicionado. Todos os IPs da listagem já existem Logic App {logic_app_name}")
        else:
            print(f"A Logic App {logic_app_name} nao possui restricoes de IP")
    else:
        print(f"Logic App {logic_app_name} nao possui restricao de ip")