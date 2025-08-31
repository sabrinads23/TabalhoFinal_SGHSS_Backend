# SGHSS App - RU 4493981
from flask import Flask, jsonify
from config import Config
from extensions import db, jwt, migrate
from routes.auth import auth_bp
from routes.administracao import administracao_bp
from routes.profissionais import profissionais_bp
from routes.pacientes import pacientes_bp
from routes.telemedicina import telemedicina_bp

def create_app():
    """
    Factory function para criar e configurar a aplicação Flask.
    """
    app = Flask(__name__) # Cria instância da aplicação
    app.config.from_object(Config) # Carrega configurações do objeto Config

    # Inicializa extensões com a aplicação
    db.init_app(app) # Banco de dados
    jwt.init_app(app) # JWT para autenticação
    migrate.init_app(app, db) # Migrations para gerenciamento do schema

    # Registro dos blueprints (módulos da aplicação)
    app.register_blueprint(auth_bp)
    app.register_blueprint(administracao_bp)
    app.register_blueprint(profissionais_bp)
    app.register_blueprint(pacientes_bp)
    app.register_blueprint(telemedicina_bp)

    # Rota simples de health check
    @app.route("/health")
    def health():
        """
        Retorna status da aplicação.
        Útil para monitoramento ou verificações de uptime.
        """
        return jsonify({"status": "ok"}), 200

    return app # Retorna a instância da aplicação configurada

# Executa a aplicação localmente quando o script é chamado diretamente
if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        from models import *  # Importa todos os modelos para garantir que o SQLAlchemy reconheça
        db.create_all() # Cria todas as tabelas no banco de dados (caso ainda não existam)
    app.run(debug=True) # Roda a aplicação em modo debug


        
        