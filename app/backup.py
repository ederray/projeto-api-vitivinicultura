"""Arquivo gerador de backup dos dados com webscrapping."""
import sys
sys.path.append('../projeto-api-vitivinicultura')
from src.utils.func_geral import salvar_arquivo
from src.utils.func_proces import obter_dados_pagina_processamento
from src.utils.func_prod_com import obter_dados_prod_com
from src.utils.func_imp_exp import obter_dados_pagina_import_export

# início do processo
print('Em execução. Capturando dados.')
# objeto que armazena os dados da pesquisa.
lista = []

# laço de repetição para armazenar todos os dados disponíveis.
for ano in list(range(2024, 2025)):
    # captura os dados da página.
    dados = obter_dados_pagina_import_export(ano:ano,processo="Importação",tag_page='05')
    # adiciona os dados na lista.
    lista.append(dados)
    print(f'{ano}: Adicionado à lista')
print('Dados inseridos com sucesso.')
# salva a colecao de dados na pasta de destino no formato json.
salvar_arquivo(lista, caminho='./data/collections_importacao4.json')

# retorno para o usuário
print('Arquivo salvo na pasta de destino.')
