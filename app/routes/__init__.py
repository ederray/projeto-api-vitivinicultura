"""Módulo de rotas da API de Vitivinicultura"""

# Import das rotas principais para facilitar o acesso
from . import auth
from . import route
from . import predict

__all__ = ["auth", "route", "predict"] 