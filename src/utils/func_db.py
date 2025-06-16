"""Arquivo de funções de conexão com o banco de dados."""
import os
import logging
from redis import Redis

# [HOTFIX] 03/06/2025 - Configuração Redis Cloud com autenticação
def setup_redis():
    """Configura Redis Cloud com tratamento de erro para ambiente de produção"""
    try:
        from config.models import MockRedis
        # Verifica se a URL completa do Redis está disponível
        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            # Usa a URL completa do Redis Cloud
            redis_client = Redis.from_url(
                redis_url, decode_responses=True, socket_connect_timeout=10)
            logging.info(
                f"✅ Tentando conectar Redis Cloud: {redis_url.split('@')[1] if '@' in redis_url else redis_url}")
        else:
            # Fallback para configuração manual
            r_host = os.getenv('REDIS_HOST', 'localhost')
            r_port = int(os.getenv('REDIS_PORT', 6379))
            r_password = os.getenv('REDIS_PASSWORD', None)
            r_username = os.getenv('REDIS_USERNAME', None)
            r_db = int(os.getenv('REDIS_DB', 0))

            redis_client = Redis(
                host=r_host,
                port=r_port,
                db=r_db,
                password=r_password,
                username=r_username,
                decode_responses=True,
                socket_connect_timeout=10
            )

            logging.info(f"✅ Tentando conectar Redis: {r_host}:{r_port}")

        # Testa a conexão
        redis_client.ping()
        logging.info("✅ Redis conectado com sucesso!")
        return redis_client

    except Exception as e:
        logging.warning(f"⚠️ Redis não disponível: {e}. Usando MockRedis.")
        return MockRedis()


def get_user_collection():
    """Função para evitar ciclo de módulos e instanciar o objeto banco de dados."""
    from config.database import user_collection
    return user_collection
