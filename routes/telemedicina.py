# Telemedicina routes - RU 4493981
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from .decorators import role_required

# Criação do blueprint para rotas de telemedicina
telemedicina_bp = Blueprint("telemedicina", __name__, url_prefix="/telemedicina")

# ---------------------- CRIAR SESSÃO DE TELEMEDICINA ----------------------
@telemedicina_bp.route("/sessao", methods=["POST"])
@jwt_required()
@role_required("profissional","admin")
def criar_sessao():
    """
    Cria uma nova sessão de telemedicina para um profissional.
    
    Requisitos:
    - Apenas usuários com role 'profissional' ou 'admin' podem criar sessões.
    - Retorna link de videochamada (simulado neste stub).

    Observação:
    - Aqui poderia haver integração com provedores de videochamada reais,
      como Jitsi, Zoom ou Whereby, usando suas APIs.
    """
    dados = request.get_json() or {}
    
    # Pega link de vídeo fornecido ou usa link padrão de demonstração
    link = dados.get("link_video", "https://example.com/vc/sessao-demo")

    # Retorna confirmação e link da sessão
    return jsonify({
        "msg": "Sessão de telemedicina criada", 
        "link_video": link
        }), 201
