""" Aplicação Fast API"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.auth import auth_router
from .routes.predict import ml_router
from .routes.route import router
from src.utils.func_auth import get_settings

# instância do objeto com as configurações de conexão 
settings = get_settings()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# construção do objeto app
app = FastAPI(
    title="API de Vitivinicultura",
    description="API para análise e previsão de dados relacionados à vitivinicultura",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração CORS para acesso as apis em diferentes conexões
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# inclusão das rotas criadas à aplicação.
app.include_router(auth_router, prefix="/auth", tags=["Autenticação"])
app.include_router(router)
app.include_router(ml_router)
