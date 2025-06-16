"""Arquivo de funções e objetos de segurança"""
from passlib.context import CryptContext

# instância do objeto de contexto de criptografia para verificar se a senha corresponde ao hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
