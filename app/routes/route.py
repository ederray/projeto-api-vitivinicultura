""""Modularização Rotas API"""
import json
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from config.models import ProducaoComercializacao, Processamento, ImportacaoExportacao, User
from config.database import data_collection
from config.schema import (obter_item_processamento_db, obter_item_prod_com_db,
                           obter_item_import_export_db)
from src.utils.func_proces import obter_dados_processamento
from src.utils.func_prod_com import obter_dados_prod_com
from src.utils.func_imp_exp import obter_dados_import_export
from src.utils.func_db import setup_redis

# Import da autenticação
from .auth import get_current_user

# instância do objeto redis para gerar o cache das rotas.
redis = setup_redis()

# construção do objeto de rota
router = APIRouter()

# construção da rota padrão
@router.get("/")
async def home():
    """Função home"""
    return (
        "Bem-vindo(a) à API de dados de Vitivinicultura da Embrapa."
        "Consulta de dados extraídas da página da Embrapa via autenticação."
        "Acesse a extensão '/docs' para mais informações."
    )

# construção da rota de produção
@router.get("/producao", status_code=201, description='Para realizar a consulta, informar os dados conforme o padrão:<br>'
            '**Ano**: 1970 a 2023.', tags=['coleta_dados'],
            response_model=ProducaoComercializacao)
async def producao(ano: int):
    """ Função que executa o scrapping dos dados de processamento."""

    # processo try-except: verifica a resposta da página.
    try:
        # pesquisa de dados em cache.
        cache = redis.get(f'{ano}-Produção')

        if cache:
            return json.loads(cache)
        else:
            # invoca a função para obter os dados da página.
            dados_web = obter_dados_prod_com(
                ano, processo='Produção', tag_page='02')
            # armazena os dados em cache.
            cache = json.dumps(dados_web)
            redis.set(f'{ano}-Produção', cache)
            # adiciona o período de tempo de armazenamento.
            redis.expire(f'{ano}-Produção', 3600)
            return dados_web
    # retorno do exception
    except HTTPException as e:
        return HTTPException(status_code=500, detail=f"Erro: {e}")
    # contingência: devolver os dados persistidos em banco
    except Exception:
        # pesquisa de dados em cache.
        cache = redis.get(f'{ano}-Produção')
        if cache:
            return json.loads(cache)
        else:
            # recupera os dados do banco de dados MongoDB.
            dados_mongo_db = data_collection.find_one(
                {'ano': ano, 'processo': 'Produção'})
            # transformação da chave id em texto para instância dos dados.
            dados_mongo_db['_id'] = str(dados_mongo_db['_id'])
            # armazena os dados em cache.
            cache = json.dumps(dados_mongo_db)
            redis.set(f'{ano}-Produção', cache)
            # adiciona o período de tempo de armazenamento.
            redis.expire(f'{ano}-Produção', 3600)
            return obter_item_prod_com_db(dados_mongo_db)

# construção da rota de processamento
@router.get("/processamento", status_code=201,
            description='Para realizar a consulta, informar os dados conforme o padrão:<br>'
            '**Ano**: 1970 a 2023.<br>'
            '**Tipo de Uva**: Viníferas:01, Americanas e Híbridas:02, Uvas de Mesa:03, '
            'Sem Classificação:04', tags=['coleta_dados'], response_model=Processamento)
async def processamento(ano: int, tipo_uva: str):
    """ Função que executa o scrapping dos dados de processamento."""

    # processo try-except: verifica a resposta da página.
    try:
        # pesquisa de dados em cache.
        cache = redis.get(f'{ano}-{tipo_uva}')

        if cache:
            return json.loads(cache)
        else:
            # invoca a função para obter os dados da página.
            dados_web = obter_dados_processamento(ano, tipo_uva)
            # armazena os dados em cache.
            cache = json.dumps(dados_web)
            redis.set(f'{ano}-{tipo_uva}', cache)
            # adiciona o período de tempo de armazenamento.
            redis.expire(f'{ano}-{tipo_uva}', 3600)
            return dados_web
    # retorno do exception
    except HTTPException as e:
        return HTTPException(status_code=500, detail=f"Erro: {e}")
    # contingência: devolver os dados persistidos em banco
    except Exception:
        # pesquisa de dados em cache.
        cache = redis.get(f'{ano}-{tipo_uva}')
        if cache:
            return json.loads(cache)
        else:
            # recupera os dados do banco de dados MongoDB.
            dados_mongo_db = data_collection.find_one({'ano': ano, 'processo': 'Processamento',
                                                       'tipo_uva': tipo_uva})
            # transformação da chave id em texto para instância dos dados.
            dados_mongo_db['_id'] = str(dados_mongo_db['_id'])
            # armazena os dados em cache.
            cache = json.dumps(dados_mongo_db)
            redis.set(f'{ano}-{tipo_uva}', cache)
            # adiciona o período de tempo de armazenamento.
            redis.expire(f'{ano}-{tipo_uva}', 3600)
            return obter_item_processamento_db(dados_mongo_db)

# construção da rota de produção
@router.get("/comercializacao", status_code=201, description='Para realizar a consulta, informar os dados conforme o padrão:<br>'
            '**Ano**: 1970 a 2023.', tags=['coleta_dados'],
            response_model=ProducaoComercializacao)
async def comercializacao(ano: int):
    """ Função que executa o scrapping dos dados de processamento."""

    # processo try-except: verifica a resposta da página.
    try:
        # pesquisa de dados em cache.
        cache = redis.get(f'{ano}-Comercialização')

        if cache:
            return json.loads(cache)
        else:
            # invoca a função para obter os dados da página.
            dados_web = obter_dados_prod_com(
                ano, processo='Comercialização', tag_page='04')
            # armazena os dados em cache.
            cache = json.dumps(dados_web)
            redis.set(f'{ano}-Comercialização', cache)
            # adiciona o período de tempo de armazenamento.
            redis.expire(f'{ano}-Comercialização', 3600)
            return dados_web
    # retorno do exception
    except HTTPException as e:
        return HTTPException(status_code=500, detail=f"Erro: {e}")
    # contingência: devolver os dados persistidos em banco
    except Exception:
        # pesquisa de dados em cache.
        cache = redis.get(f'{ano}-Comercialização')
        if cache:
            return json.loads(cache)
        else:
            # recupera os dados do banco de dados MongoDB.
            dados_mongo_db = data_collection.find_one(
                {'ano': ano, 'processo': 'Comercialização'})
            # transformação da chave id em texto para instância dos dados.
            dados_mongo_db['_id'] = str(dados_mongo_db['_id'])
            # armazena os dados em cache.
            cache = json.dumps(dados_mongo_db)
            redis.set(f'{ano}-Comercialização', cache)
            # adiciona o período de tempo de armazenamento.
            redis.expire(f'{ano}-Comercialização', 3600)
            return obter_item_prod_com_db(dados_mongo_db)

# construção da rota de importação
@router.get("/importacao", status_code=201,
            description='Para realizar a consulta, informar os dados conforme o padrão:<br>'
            '**Ano**: 1970 a 2024.<br>'
            '**Derivados**: Vinhos de mesa:01, Espumantes:02, Uvas frescas:03,'
            'Uvas passas:04, Suco de uva:05', tags=['coleta_dados'], response_model=ImportacaoExportacao)
async def importacao(ano: int, derivado: str):
    """ Função que executa o scrapping dos dados de processamento."""

    # processo try-except: verifica a resposta da página.
    try:
        # pesquisa de dados em cache.
        cache = redis.get(f'{ano}-{derivado}-Importação')

        if cache:
            return json.loads(cache)
        else:
            # invoca a função para obter os dados da página.
            dados_web = obter_dados_import_export(ano, derivado, processo='Importação',
                                                  tag_page='05')
            # armazena os dados em cache.
            cache = json.dumps(dados_web)
            redis.set(f'{ano}-{derivado}-Importação', cache)
            # adiciona o período de tempo de armazenamento.
            redis.expire(f'{ano}-{derivado}-Importação', 3600)
            return dados_web
    # retorno do exception
    except HTTPException as e:
        return HTTPException(status_code=500, detail=f"Erro: {e}")
    # contingência: devolver os dados persistidos em banco
    except Exception:
        # pesquisa de dados em cache.
        cache = redis.get(f'{ano}-{derivado}-Importação')
        if cache:
            return json.loads(cache)
        else:
            # recupera os dados do banco de dados MongoDB.
            dados_mongo_db = data_collection.find_one({'ano': ano, 'processo': 'Importação',
                                                       'produto': derivado})
            # transformação da chave id em texto para instância dos dados.
            dados_mongo_db['_id'] = str(dados_mongo_db['_id'])
            # armazena os dados em cache.
            cache = json.dumps(dados_mongo_db)
            redis.set(f'{ano}-{derivado}-Importação', cache)
            # adiciona o período de tempo de armazenamento.
            redis.expire(f'{ano}-{derivado}-Importação', 3600)
            return obter_item_import_export_db(dados_mongo_db)

# construção da rota de exportação
@router.get("/exportacao", status_code=201,
            description='Para realizar a consulta, informar os dados conforme o padrão:<br>'
            '**Ano**: 1970 a 2024.<br>'
            '**Derivados**: Vinhos de mesa:01, Espumantes:02, Uvas frescas:03, Suco de uva:04', tags=['coleta_dados'], response_model=ImportacaoExportacao)
async def exportacao(ano: int, derivado: str):
    """ Função que executa o scrapping dos dados de processamento."""

    # processo try-except: verifica a resposta da página.
    try:
        # pesquisa de dados em cache.
        cache = redis.get(f'{ano}-{derivado}-Exportação')

        if cache:
            return json.loads(cache)
        else:
            # invoca a função para obter os dados da página.
            dados_web = obter_dados_import_export(ano, derivado, processo='Exportação',
                                                  tag_page='06')
            # armazena os dados em cache.
            cache = json.dumps(dados_web)
            redis.set(f'{ano}-{derivado}-Exportação', cache)
            # adiciona o período de tempo de armazenamento.
            redis.expire(f'{ano}-{derivado}-Exportação', 3600)
            return dados_web
    # retorno do exception
    except HTTPException as e:
        return HTTPException(status_code=500, detail=f"Erro: {e}")
    # contingência: devolver os dados persistidos em banco
    except Exception:
        # pesquisa de dados em cache.
        cache = redis.get(f'{ano}-{derivado}-Exportação')
        if cache:
            return json.loads(cache)
        else:
            # recupera os dados do banco de dados MongoDB.
            dados_mongo_db = data_collection.find_one({'ano': ano, 'processo': 'Exportação',
                                                       'produto': derivado})
            # transformação da chave id em texto para instância dos dados.
            dados_mongo_db['_id'] = str(dados_mongo_db['_id'])
            # armazena os dados em cache.
            cache = json.dumps(dados_mongo_db)
            redis.set(f'{ano}-{derivado}-Exportação', cache)
            # adiciona o período de tempo de armazenamento.
            redis.expire(f'{ano}-{derivado}-Exportação', 3600)
            return obter_item_import_export_db(dados_mongo_db)
