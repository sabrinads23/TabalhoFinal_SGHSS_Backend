# Administracao routes - RU 4493981
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from extensions import db
from models.administracao import Leito, Internacao, RelatorioFinanceiro, Suprimento
from models.pacientes import Paciente
from models.profissionais import Profissional
from datetime import datetime

from models.usuarios import Usuario
from .decorators import role_required

# Cria um blueprint para agrupar todas as rotas de administração
administracao_bp = Blueprint("administracao", __name__, url_prefix="/administracao")

# Função auxiliar para obter o ID do usuário a partir do JWT
def get_user_id():
    identity = get_jwt_identity()
    try:
        return int(identity)
    except (TypeError, ValueError):
        return identity

# ---------------------- LISTAR ADMINISTRADORES----------------------
@administracao_bp.route("/administradores", methods=["GET"])
def listar_administradores():
    # Retorna todos os usuários com role "admin"
    administradores = Usuario.query.filter_by(role="admin").all()
    result = []
    for a in administradores:
        result.append({
            "id": a.id,
            "nome": a.nome,
            "email": a.email,
            "role": a.role
        })
    return jsonify(result), 200

# ---------------------- CADASTRAR PACIENTE ----------------------
@administracao_bp.route("/admin/pacientes", methods=["POST"])
@jwt_required()
@role_required("admin") # Apenas administradores podem cadastrar
def cadastrar_paciente_admin():
    data = request.get_json()
    # Verifica se CPF já está cadastrado
    paciente_existente = Paciente.query.filter_by(cpf=data['cpf']).first()
    if paciente_existente:
        return jsonify({"msg": "Paciente já cadastrado com este CPF"}), 400
    
    #Cria o paciente
    _ = get_user_id()
    dados = request.get_json() or {}
    p = Paciente(
        nome=dados["nome"],
        cpf=dados["cpf"],
        data_nascimento=datetime.strptime(data['data_nascimento'], "%Y-%m-%d").date(),
        telefone=dados.get("telefone"),
        email=dados.get("email"),
        senha=generate_password_hash(dados["senha"]), # Criptografa senha
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({"msg": "Paciente cadastrado com sucesso!", "id": p.id}), 201

# ---------------------- LISTAR PACIENTES ----------------------
@administracao_bp.route("/pacientes", methods=["GET"])
@jwt_required()
@role_required("admin")
def listar_pacientes():
    pacientes = Paciente.query.all()
    result = []
    for p in pacientes:
        result.append({
            "id": p.id,
            "nome": p.nome,
            "cpf": p.cpf,
            "email": p.email,      
            "data_nascimento": p.data_nascimento.strftime("%Y-%m-%d") if p.data_nascimento else None,
            "telefone": p.telefone
        })
    return jsonify(result), 200

# ---------------------- CADASTRAR PROFISSIONAIS ----------------------
@administracao_bp.route("/admin/profissionais", methods=["POST"])
@jwt_required()
@role_required("admin")
def cadastrar_profissional_admin():
    data = request.get_json()
    # Verificar se já existe profissional com mesmo CRM
    if data.get("crm"):
        profissional_existente = Profissional.query.filter_by(crm=data["crm"]).first()
        if profissional_existente:
            return jsonify({"msg": "Profissional já cadastrado com este CRM"}), 400
    
    # Verificar se já existe profissional com mesmo Email
    if data.get("email"):
        email_existente = Profissional.query.filter_by(email=data["email"]).first()
        if email_existente:
            return jsonify({"msg": "Já existe um profissional cadastrado com este Email"}), 400
    
    #Cria o profissional
    _ = get_user_id()
    dados = request.get_json() or {}
    prof = Profissional(
        nome=dados["nome"],
        crm=dados.get("crm"),
        especialidade=dados.get("especialidade"),
        email=dados["email"],
        senha = generate_password_hash(dados.get("senha")), 
        tipo=dados.get("tipo","medico")
    )
    db.session.add(prof)
    db.session.commit()
    return jsonify({"msg": "Profissional cadastrado com sucesso!", "id": prof.id}), 201

# ---------------------- LISTAR PROFISSIONAIS ----------------------
@administracao_bp.route("/profissionais", methods=["GET"])
@jwt_required()
@role_required("admin")
def listar_profissionais():
    profissionais = Profissional.query.all()
    result = []
    for prof in profissionais:
        result.append({
            "id": prof.id,
            "nome": prof.nome,
            "tipo": prof.tipo,
            "crm": prof.crm
        })
    return jsonify(result), 200

# ---------------------- CADASTRAR LEITOS ----------------------
@administracao_bp.route("/leitos", methods=["POST"])
@jwt_required()
@role_required("admin")
def cadastrar_leito():
    data = request.get_json()
    # Verificar se já existe leito com mesmo número
    if data.get("numero"):
        leito_existente = Leito.query.filter_by(numero=data["numero"]).first()
        if leito_existente:
            return jsonify({"msg": "Já existe um leito cadastrado com este número"}), 400

    #Cria o leito
    _ = get_user_id()
    l = Leito(numero=data["numero"], tipo=data.get("tipo"))
    db.session.add(l)
    db.session.commit()
    return jsonify({"msg": "Leito cadastrado com sucesso!", "id": l.id}), 201

# ---------------------- LISTAR LEITOS ----------------------
@administracao_bp.route("/leitos", methods=["GET"])
@jwt_required()
@role_required("admin")
def listar_leitos():
    _ = get_user_id()
    leitos = Leito.query.all()
    resultado = []

    for l in leitos:
        # Verifica se há uma internação ativa nesse leito
        internacao_ativa = Internacao.query.filter_by(leito_id=l.id, data_fim=None).first()

        resultado.append({
            "id": l.id,
            "numero": l.numero,
            "tipo": l.tipo,
            "ocupado": "Sim" if internacao_ativa else "Não",
            "paciente_id": internacao_ativa.paciente_id if internacao_ativa else None
        })

    return jsonify(resultado), 200

# ---------------------- INICIAR INTERNAÇÃO ----------------------
@administracao_bp.route("/internacoes", methods=["POST"])
@jwt_required()
@role_required("admin")
def iniciar_internacao():
    _ = get_user_id()
    dados = request.get_json() or {}
    # Verifica se o leito existe
    leito = Leito.query.get(dados["leito_id"])
    if not leito:
        return jsonify({"msg": "Leito não encontrado"}), 404

    # Verifica se já está ocupado
    if leito.ocupado:
        return jsonify({"msg": "Leito ocupado"}), 400

    # Verifica se o paciente existe
    paciente = Paciente.query.get(dados["paciente_id"])
    if not paciente:
        return jsonify({"msg": "Paciente não encontrado"}), 404

    # Cria a internação
    leito.ocupado = True
    intern = Internacao(paciente_id=paciente.id, leito_id=leito.id)
    db.session.add(intern)
    db.session.commit()

    return jsonify({
        "msg": "Internação iniciada",
        "id": intern.id,
        "paciente": paciente.nome,
        "leito_id": leito.id
    }), 201

# ---------------------- ENCERRAR INTERNAÇÃO ----------------------
@administracao_bp.route("/internacoes/<int:id>/alta", methods=["PUT"])
@jwt_required()
@role_required("admin")
def encerrar_internacao(id):
    _ = get_user_id()
    
    # Verifica se a internação existe
    intern = Internacao.query.get(id)
    if not intern:
        return jsonify({"msg": "Internação não encontrada"}), 404

    # Se já foi encerrada
    if intern.data_fim is not None:
        return jsonify({"msg": "Esta internação já foi encerrada"}), 400

    # Verifica se o paciente existe
    paciente = Paciente.query.get(intern.paciente_id)
    if not paciente:
        return jsonify({"msg": "Paciente não encontrado para esta internação"}), 404

    # Verifica se o leito existe
    leito = Leito.query.get(intern.leito_id)
    if not leito:
        return jsonify({"msg": "Leito não encontrado para esta internação"}), 404

    # Encerrar a internação
    intern.data_fim = datetime.utcnow()
    leito.ocupado = False
    db.session.commit()

    return jsonify({
        "msg": "Internação encerrada. Alta do paciente.",
        "internacao_id": intern.id,
        "paciente": paciente.nome,
        "leito_id": leito.id
    }), 200

# ---------------------- LISTAR INTERNAÇÕES ----------------------
@administracao_bp.route("/internacoes", methods=["GET"])
@jwt_required()
@role_required("admin")
def listar_internacoes():
    internacoes = Internacao.query.all()
    result = []
    for i in internacoes:
        result.append({
            "id": i.id,
            "paciente_id": i.paciente_id,
            "leito_id": i.leito_id,
            "data_inicio": i.data_inicio.strftime("%Y-%m-%d %H:%M:%S") if i.data_inicio else None,
            "data_fim": i.data_fim.strftime("%Y-%m-%d %H:%M:%S") if i.data_fim else None,
            "status": "Ativa" if not i.data_fim else "Encerrada"
        })
    return jsonify(result), 200

# ---------------------- CADASTRAR SUPRIMENTOS ----------------------
@administracao_bp.route("/suprimentos", methods=["POST"])
@jwt_required()
@role_required("admin")
def cadastrar_suprimento():
    _ = get_user_id()
    dados = request.get_json() or {}
    s = Suprimento(nome=dados["nome"], quantidade=dados.get("quantidade", 0), descricao=dados.get("descricao"))
    db.session.add(s)
    db.session.commit()
    return jsonify({"msg": "Suprimento cadastrado", "id": s.id}), 201

# ---------------------- LISTAR SUPRIMENTOS ----------------------
@administracao_bp.route("/suprimentos", methods=["GET"])
@jwt_required()
@role_required("admin")
def listar_suprimentos():
    _ = get_user_id()
    suprimentos = Suprimento.query.all()

    resultado = []
    for s in suprimentos:
        resultado.append({
            "id": s.id,
            "nome": s.nome,
            "quantidade": s.quantidade,
            "descricao": s.descricao if hasattr(s, "descricao") else None
        })

    return jsonify(resultado), 200

# ---------------------- DELETAR SUPRIMENTOS ----------------------
@administracao_bp.route("/suprimentos/<int:id>", methods=["DELETE"])
@jwt_required()
@role_required("admin")
def deletar_suprimento(id):
    _ = get_user_id()
    
    # Verifica se o suprimento existe
    suprimento = Suprimento.query.get(id)
    if not suprimento:
        return jsonify({"msg": "Suprimento não encontrado"}), 404

    # Remove o suprimento
    db.session.delete(suprimento)
    db.session.commit()

    return jsonify({"msg": "Suprimento removido com sucesso", "id": id}), 200

# ---------------------- ADICIONAR RELATORIOS ----------------------
@administracao_bp.route("/admin/relatorios", methods=["POST"])
@jwt_required()
@role_required("admin")
def adicionar_relatorio():
    _ = get_user_id()
    dados = request.get_json() or {}
    r = RelatorioFinanceiro(tipo=dados["tipo"], descricao=dados["descricao"], valor=dados["valor"])
    db.session.add(r)
    db.session.commit()
    return jsonify({"msg": "Relatório financeiro registrado com sucesso!", "id": r.id}), 201

# ---------------------- LISTAR RELATORIOS ----------------------
@administracao_bp.route("/admin/relatorios", methods=["GET"])
@jwt_required()
@role_required("admin")
def listar_relatorios():
    _ = get_user_id()
    tipo = request.args.get("tipo")
    q = RelatorioFinanceiro.query
    if tipo:
        q = q.filter_by(tipo=tipo)
    relatorios = q.all()
    return jsonify([{
        "id": r.id,
        "tipo": r.tipo,
        "descricao": r.descricao,
        "valor": r.valor,
        "data": r.data.strftime("%Y-%m-%d %H:%M")
    } for r in relatorios])
