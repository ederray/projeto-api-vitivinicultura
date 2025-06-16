"""Arquivo de funções de autenticação."""
from datetime import datetime, timedelta
from typing import Annotated
from functools import lru_cache
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from config.settings import Settings
from src.utils.func_db import get_user_collection

# instância do objeto
logger = logging.getLogger(__name__)

# instância do objeto OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# função para armazenar os dados da classe settings em cache.
@lru_cache()
def get_settings() -> Settings:
    return Settings()

# [AUTH] 30/05/2025 - Função adicionada para suportar autenticação de usuários.
async def get_user_by_username(username: str):
    """Função que retorna os dodos de usuário inseridos no banco de dados."""
    from config.models import User
    try:
        user_data = get_user_collection().find_one({"username": username})
        if user_data:
            return User(username=user_data["username"],
                        hashed_password=user_data["hashed_password"])
        return None
    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        return None


# [AUTH] 30/05/2025 - Funções de gerenciamento de tokens JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Função para criar o token de acesso."""
    settings = get_settings()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

# função para retornar o usuário atual
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Função para selecionar retornar o usuário conectado."""
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user
