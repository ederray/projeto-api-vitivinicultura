'''Arquivo gerador de backup no banco de dados MongoDB.'''
import sys
import os
sys.path.append("../projeto-api-vitivinicultura")
from src.utils.func_geral import salvar_dados_db

# seleciona a coleção de dados para salvar no banco de dados.
salvar_dados_db('data/raw/collections/collections_producao.json', processo='Produção')

# retorno para o usuário
print('Dados salvos com sucesso.')
