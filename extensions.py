# Extensions - RU 4493981

# Importa a classe responsável pelo ORM (Object Relational Mapper),
# que permite mapear modelos Python em tabelas do banco de dados.
from flask_sqlalchemy import SQLAlchemy

# Importa a classe que gerencia o JWT (JSON Web Token),
# usada para autenticação e autorização de usuários.
from flask_jwt_extended import JWTManager

# Importa a ferramenta de migração de banco de dados,
# que auxilia na criação e atualização do schema do banco (ex: tabelas e colunas).
from flask_migrate import Migrate

# Instância global do banco de dados que será inicializada no app principal.
db = SQLAlchemy()

# Instância global do gerenciador de autenticação JWT.
jwt = JWTManager()

# Instância global do gerenciador de migrações de banco de dados.
migrate = Migrate()
