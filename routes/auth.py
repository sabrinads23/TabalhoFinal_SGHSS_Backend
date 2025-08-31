# Auth routes - RU 4493981
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models.usuarios import Usuario

# Cria um blueprint para agrupar todas as rotas de autenticação
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Rota para registrar um novo usuário no sistema.
    Recebe JSON com: nome, email, senha e role (opcional, padrão = paciente).
    """
    dados = request.get_json() or {}
    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")
    role = dados.get("role", "paciente")

    # Validação: todos os campos obrigatórios devem ser informados
    if not all([nome, email, senha]):
        return jsonify({"msg": "nome, email, senha são obrigatórios"}), 400
    
    # Validação: email não pode estar duplicado
    if Usuario.query.filter_by(email=email).first():
        return jsonify({"msg": "Email já cadastrado"}), 409
    
    # Criação do usuário com senha criptografada
    u = Usuario(nome=nome, email=email, senha=generate_password_hash(senha), role=role)
    db.session.add(u)
    db.session.commit()

    # Retorna sucesso e ID do usuário criado
    return jsonify({"msg": "Usuário criado", "id": u.id}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Rota para autenticar o usuário e gerar token JWT.
    Recebe JSON com: email e senha.
    """
    dados = request.get_json() or {}
    email = dados.get("email")
    senha = dados.get("senha")

    # Validação: campos obrigatórios
    if not email or not senha:
        return jsonify({"msg": "Email e senha são obrigatórios"}), 400
    
    # Verifica se o usuário existe e se a senha está correta
    u = Usuario.query.filter_by(email=email).first()
    if not u or not check_password_hash(u.senha, senha):
        return jsonify({"msg": "Credenciais inválidas"}), 401
    
    # Criação de claims adicionais para o token
    claims = {"role": u.role, "email": u.email}

    # Gera o token JWT
    token = create_access_token(identity=str(u.id), additional_claims=claims)

    # Retorna token e dados do usuário
    return jsonify({"access_token": token, "usuario": {"id": u.id, "nome": u.nome, "email": u.email, "role": u.role}}), 200
