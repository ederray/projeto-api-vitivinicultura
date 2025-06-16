"""Rotas de autenticação"""
# [AUTH] 30/05/2025 - Módulo criado para implementar autenticação JWT com FastAPI
from datetime import timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from config.models import User, UserCreate, UserResponse, Token, TokenRequest
from src.utils.func_db import get_user_collection
from src.utils.func_auth import *
from src.utils.func_security import pwd_context

# construção do objeto de rota
auth_router = APIRouter()

# instância do objeto com as configurações de conexão
settings = get_settings()


# [AUTH] 30/05/2025 - Rota de registro de novos usuários
@auth_router.post("/signup", response_model=UserResponse, summary="Cadastro - Criar Nova Conta")
async def create_user(user: UserCreate):
    """
    Cria uma nova conta de usuário.

    Regras:
    - Username: 3-50 caracteres, apenas letras, números, _ ou -
    - Senha: mínimo 6 caracteres, deve conter pelo menos 1 letra e 1 número
    """
    # Verifica se o usuário já existe
    existing_user = await get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já está em uso"
        )

    # Cria o hash da senha
    hashed_password = pwd_context.hash(user.password)

    # Cria o usuário no banco
    user_dict = {
        "username": user.username,
        "hashed_password": hashed_password
    }
    # insere o usuário no banco de dados.
    get_user_collection().insert_one(user_dict)

    # retorno para o usuário.
    return {
        "username": user.username,
        "message": "Usuário criado com sucesso! Use /auth/token para fazer login."
    }


# [DEPLOY] 03/06/2025 - Rota de login melhorada para compatibilidade com Swagger
@auth_router.post("/token", response_model=Token, summary="Login - Obter Token JWT")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    grant_type: Optional[str] = Form(default="password"),
    scope: str = Form(default=""),
    client_id: Optional[str] = Form(default=None),
    client_secret: Optional[str] = Form(default=None)
):
    """
    Faz login e retorna um token JWT.

    Envie username e password via form-data.
    O token retornado deve ser usado no header: Authorization: Bearer {token}
    """
    user = await get_user_by_username(username.lower())
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # limite de tempo de expiração do token
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# [DEPLOY] 03/06/2025 - Endpoint adicional de login usando JSON para testes diretos
@auth_router.post("/login", response_model=Token, summary="Login Alternativo - JSON")
async def login_json(request: TokenRequest):
    """
    Login alternativo usando JSON (para testes com curl/Postman)
    """
    user = await get_user_by_username(request.username.lower())
    if not user or not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Rota protegida para testar autenticação
@auth_router.get("/me", response_model=dict, summary="Perfil - Dados do Usuário Logado")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Retorna informações do usuário autenticado.

    Requer token JWT no header: Authorization: Bearer {token}
    """
    return {
        "username": current_user.username,
        "message": "Usuário autenticado com sucesso!"
    }
