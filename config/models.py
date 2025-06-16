"""Modelo de Dados"""
import os
import regex as re
from typing import List
from pydantic import BaseModel, Field, validator
from src.utils.func_security import pwd_context


class Processamento(BaseModel):
    """Classe que recebe os dados de Processamento."""
    ano: int
    processo: str
    tipo_uva: str
    tipo_uva_texto: str
    labels: List[str]
    data: List[List[str]]


class ProducaoComercializacao(BaseModel):
    """Classe que recebe os dados de Produção e Comercialização."""
    ano: int
    processo: str
    labels: List[str]
    data: List[List[str]]


class ImportacaoExportacao(BaseModel):
    """Classe que recebe os dados de Importação e Exportação."""
    ano: int
    processo: str
    produto: str
    produto_texto: str
    labels: List[str]
    data: List[List[str]]

    def expand_data(self):
        """ Função que retorna os dados de forma de lista para transformação tabular."""
        linhas = []
        for linha in self.data:
            linha_dict = {
                'ano': self.ano,
                'processo': self.processo,
                'produto': self.produto,
                'produto_texto': self.produto_texto,
                self.labels[0]: linha[0],
                self.labels[1]: linha[1],
                self.labels[2]: linha[2],
            }
            linhas.append(linha_dict)
        return linhas


class User(BaseModel):
    """Classe que recebe os dados de usuário das apis de autenticação."""
    username: str
    hashed_password: str

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)
    
class CategoriasRequest(BaseModel):
    """Classe que recebe o tipo de dado da requisição do modelo ML."""
    categorias: int

# [AUTH] 30/05/2025 - Modelos Pydantic para autenticação
class Token(BaseModel):
    """Classe que recebe os dados de token do usuário."""
    access_token: str
    token_type: str


class TokenRequest(BaseModel):
    """Classe que recebe a requisição de token do usuário"""
    username: str
    password: str


class UserCreate(BaseModel):
    """Classe que recebe os dados de criação de usuário"""
    username: str = Field(..., min_length=3, max_length=50,
                          description="Nome de usuário (3-50 caracteres)")
    password: str = Field(..., min_length=6,
                          description="Senha com pelo menos 6 caracteres, "
                          "incluindo letras e números")
    # validação de usuário

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError(
                'Username deve conter apenas letras, números, _ ou -')
        return v.lower()

    # validação de senha
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Senha deve ter pelo menos 6 caracteres')

        # Verifica se tem pelo menos uma letra
        if not re.search(r'[a-zA-Z]', v):
            raise ValueError('Senha deve conter pelo menos uma letra')

        # Verifica se tem pelo menos um número
        if not re.search(r'\d', v):
            raise ValueError('Senha deve conter pelo menos um número')

        return v


class UserResponse(BaseModel):
    """Classe que recebe os dados de usuário como resposta do banco de dados."""
    username: str
    message: str

class MockRedis:
    """Mock do Redis para quando não estiver disponível"""

    def __init__(self):
        self.data = {}

    def get(self, key):
        return None

    def set(self, key, value):
        return True

    def expire(self, key, seconds):
        return True

    def ping(self):
        return True
