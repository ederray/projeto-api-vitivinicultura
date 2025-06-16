"""Settings"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Classe que recebe os parâmetros de conexão das aplicações."""
    # MongoDB
    DB_URI: str

    # JWT
    JWT_SECRET_KEY: str = "default-insecure-key-change-it"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Redis
    REDIS_URL: str

    # API Settings
    API_ENV: str = "development"
    DEBUG: bool = True

    # CORS - permite todas as origens em produção para facilitar testes
    CORS_ORIGINS: List[str] = ["*"]

    # Configurações específicas do Render
    PORT: int = 8000

    class Config:
        env_file = ".env"

# instância do objeto settings
settings = Settings()