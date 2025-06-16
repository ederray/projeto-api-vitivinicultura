"""Database"""
import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()  # garante que .env seja carregado

# Configurar logging
logger = logging.getLogger(__name__)

# constante de conexão com o servidor MongoDB.
URI = os.getenv('DB_URI')

# criação de um cliente para conexão com o servidor.
client = MongoClient(URI)

# construção dos database que recebe as coleções de dados
db = client.api

# construção de uma coleção que recebe os dados dos usuários do sistema para verificação.
user_collection = db.users

# construção de uma coleção que recebe os dados do processo de webscrapping.
data_collection = db.data
