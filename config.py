# SGHSS Starter Config - RU 4493981
import os

class Config:
    """
    Classe de configuração da aplicação Flask.
    Contém todas as variáveis necessárias para o SGHSS funcionar.
    """

    # Chave secreta da aplicação (usada para sessões e criptografia)
    # Tenta pegar da variável de ambiente, senão usa valor padrão (apenas para dev)
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    # URI de conexão com o banco de dados
    # Pode ser configurado via variável de ambiente DATABASE_URL
    # Caso não exista, cria um banco SQLite local chamado sghss.db
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///sghss.db")

    # Desativa o rastreamento de modificações do SQLAlchemy (economiza memória)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Chave secreta usada para gerar tokens JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")

    # Propaga exceções para o Flask lidar corretamente
    PROPAGATE_EXCEPTIONS = True

    # Tempo de expiração do token de acesso JWT em segundos (4 horas)
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 4  # 4 hours
