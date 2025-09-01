# Pacientes routes - RU 4493981
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import check_password_hash
from extensions import db
from models.pacientes import Paciente
from models.agendas import Agenda, Horario
from models.consulta import Consulta
from .decorators import role_required
from models.exames import Exame
from models.notificacoes import Notificacao
from datetime import datetime
from flask import jsonify

# Cria um blueprint para rotas de paciente
pacientes_bp = Blueprint("pacientes", __name__, url_prefix="/pacientes")

# ---------------------- LOGIN PACIENTE ----------------------
@pacientes_bp.route("/login", methods=["POST"])
def login_paciente():
    """
    Autenticação de paciente.
    Recebe JSON com email e senha.
    Retorna token JWT e ID do paciente.
    """
    dados = request.get_json() or {}
    email = dados.get("email")
    senha = dados.get("senha")

    # Se campos não preenchidos
    if not email or not senha:
        return jsonify({"msg": "Email e senha são obrigatórios"}), 400

    paciente = Paciente.query.filter_by(email=email).first()

    # Se campos preenchidos incorretamente
    if not paciente or not check_password_hash(paciente.senha, senha):
        return jsonify({"msg": "Credenciais inválidas"}), 401

    # Gera o token JWT
    token = create_access_token(
        identity=str(paciente.id),
        additional_claims={"tipo": "paciente"} # identifica o tipo de usuário no token
    )

    # Retorna token e dados do usuário
    return jsonify({
        "access_token": token,
        "paciente_id": paciente.id
    }), 200


# ---------------------- LISTAR TODOS OS HORÁRIOS DISPONÍVEIS ----------------------
@pacientes_bp.route("/agendas/horarios", methods=["GET"])
@jwt_required()
def listar_todos_horarios():
    """
    Retorna todos os horários disponíveis em todas as agendas.
    """
    agendas = Agenda.query.order_by(Agenda.data, Agenda.profissional_id).all()

    resultado = []
    for agenda in agendas:
        horarios = Horario.query.filter_by(agenda_id=agenda.id, disponivel=True).order_by(Horario.hora).all()
        if not horarios:
            continue  # pula agendas sem horários disponíveis
        resultado.append({
            "agenda_id": agenda.id,
            "data": agenda.data.strftime("%Y-%m-%d"),
            "profissional_id": agenda.profissional_id,
            "horarios": [{"id": h.id, "hora": h.hora.strftime("%H:%M:%S")} for h in horarios]
        })

    return jsonify(resultado), 200

# ---------------------- MARCAR CONSULTA ----------------------
@pacientes_bp.route("/consultas", methods=["POST"])
@jwt_required()
def marcar_consulta():
    """
    Permite que o paciente marque uma consulta em um horário disponível.
    Recebe: agenda_id, horario, paciente_id
    """
    data = request.get_json()
    agenda_id = data.get("agenda_id")
    hora_escolhida = data.get("horario")
    paciente_id = data.get("paciente_id")

    # Valida campos obrigatórios
    if not all([agenda_id, hora_escolhida, paciente_id]):
        return jsonify({"msg": "agenda_id, horario e paciente_id são obrigatórios"}), 400

    # Verifica se o paciente existe
    paciente = Paciente.query.get(paciente_id)
    if not paciente:
        return jsonify({"msg": f"Paciente com id {paciente_id} não encontrado"}), 404

    # Verifica se a agenda existe
    agenda = Agenda.query.get(agenda_id)
    if not agenda:
        return jsonify({"msg": f"Agenda com id {agenda_id} não encontrada"}), 404

    # Converte string para objeto time
    try:
        # Se o JSON vier como "09:00" ou "09:00:00", ajusta o formato
        hora_obj = datetime.strptime(hora_escolhida, "%H:%M").time()
    except ValueError:
        try:
            hora_obj = datetime.strptime(hora_escolhida, "%H:%M:%S").time()
        except ValueError:
            return jsonify({"msg": "Formato de horário inválido. Use HH:MM ou HH:MM:SS"}), 400

    # Busca horário disponível
    horario = Horario.query.filter_by(
        agenda_id=agenda_id, hora=hora_obj, disponivel=True
    ).first()
    if not horario:
        return jsonify({"msg": "Horário não disponível"}), 400

    # Bloqueia horário
    horario.disponivel = False

    # Cria registro da consulta
    consulta = Consulta(
        paciente_id=paciente_id,
        profissional_id=agenda.profissional_id,
        agenda_id=agenda_id,
        horario_id=horario.id,
        data_consulta=agenda.data,
        hora_consulta=hora_obj,
        status="Agendada",
    )

    db.session.add(consulta)
    db.session.commit()

    return jsonify({
        "msg": "Consulta marcada com sucesso",
        "consulta_id": consulta.id,
        "paciente_id": paciente_id,
        "profissional_id": consulta.profissional_id,
        "data": str(consulta.data_consulta),
        "hora": consulta.hora_consulta.strftime("%H:%M:%S"),
        "status": consulta.status
    }), 201

# ---------------------- CANCELAR CONSULTA ----------------------
@pacientes_bp.route("/consultas/<consulta_id>/cancelar", methods=["PUT"])
@jwt_required()
def cancelar_consulta(consulta_id):
    """
    Permite cancelar uma consulta. Libera o horário novamente.
    """

    # Verifica se o ID foi preenchido e se é um número válido
    if not consulta_id.isdigit():
        return jsonify({"msg": "É necessário informar um ID de consulta válido na rota"}), 400

    consulta_id = int(consulta_id)

    # Verifica se a consulta existe
    consulta = Consulta.query.get(consulta_id)
    if not consulta:
        return jsonify({"msg": f"Consulta com id {consulta_id} não encontrada"}), 404

    # Verifica se a consulta já foi cancelada
    if consulta.status == "Cancelada":
        return jsonify({"msg": "Essa consulta já foi cancelada"}), 400

    # Libera o horário novamente
    horario = Horario.query.get(consulta.horario_id)
    if horario:
        horario.disponivel = True

    consulta.status = "Cancelada"
    db.session.commit()

    return jsonify({
        "msg": "Consulta cancelada com sucesso",
        "consulta_id": consulta.id,
        "status": consulta.status
    }), 200

# ---------------------- REMARCAR CONSULTA ----------------------
@pacientes_bp.route("/consultas/<int:consulta_id>/remarcar", methods=["PUT"])
@jwt_required()
def remarcar_consulta(consulta_id):
    """
    Permite remarcar uma consulta existente.
    Recebe novo_horario_id. Atualiza a consulta e libera o horário antigo.
    """
    data = request.get_json()
    novo_horario_id = data.get("novo_horario_id")

    if not novo_horario_id:
        return jsonify({"msg": "novo_horario_id é obrigatório"}), 400

    consulta = Consulta.query.get_or_404(consulta_id)

    if consulta.status != "Agendada":
        return jsonify({"msg": "Somente consultas agendadas podem ser remarcadas"}), 400

    # Libera o horário antigo
    horario_antigo = Horario.query.get(consulta.horario_id)
    if horario_antigo:
        horario_antigo.disponivel = True

    # Verifica se o novo horário existe
    novo_horario = Horario.query.get(novo_horario_id)
    if not novo_horario:
        return jsonify({"msg": f"Horário com id {novo_horario_id} não encontrado"}), 404

    # Verifica se o novo horário está disponível
    if not novo_horario.disponivel:
        return jsonify({"msg": "Novo horário indisponível"}), 400

    # Verifica se o novo horário pertence ao mesmo profissional da consulta
    if novo_horario.agenda.profissional_id != consulta.profissional_id:
        return jsonify({"msg": "O novo horário não pertence ao mesmo profissional"}), 400

    # Atualiza a consulta
    consulta.horario_id = novo_horario_id
    novo_horario.disponivel = False
    db.session.commit()

    return jsonify({
        "msg": "Consulta remarcada com sucesso",
        "consulta_id": consulta.id,
        "novo_horario_id": novo_horario.id,
        "profissional_id": consulta.profissional_id,
        "status": consulta.status
    }), 200

# ---------------------- HISTORICO DE CONSULTAS ----------------------
@pacientes_bp.route("/consultas/historico/<int:paciente_id>", methods=["GET"])
@jwt_required()
def historico_consultas(paciente_id=None):
    """
    Retorna o histórico de consultas de um paciente.
    Verifica role para acesso seguro (paciente só acessa seu próprio histórico).
    """
    from flask_jwt_extended import get_jwt_identity, get_jwt

    # Verifica se foi passado o ID do paciente
    if paciente_id is None:
        return jsonify({"msg": "O parâmetro paciente_id é obrigatório"}), 400

    # Busca paciente
    paciente = Paciente.query.get(paciente_id)
    if not paciente:
        return jsonify({"msg": f"Paciente com id {paciente_id} não encontrado"}), 404

    # Verifica role
    claims = get_jwt()
    tipo_usuario = claims.get("tipo")  # "paciente" ou "admin"
    user_id = get_jwt_identity()

    if tipo_usuario == "paciente" and int(user_id) != paciente_id:
        return jsonify({
            "msg": "Acesso negado",
            "required": ["paciente", "admin"],
            "role": tipo_usuario
        }), 403

    # Busca todas as consultas do paciente
    consultas = Consulta.query.filter_by(paciente_id=paciente_id).all()
    
    if not consultas:
        return jsonify({"msg": f"Paciente {paciente_id} não possui consultas cadastradas"}), 200

    return jsonify([{
        "id": c.id,
        "profissional_id": c.profissional_id,
        "data": str(c.data_consulta),
        "hora": c.hora_consulta.strftime("%H:%M:%S"),
        "status": c.status
    } for c in consultas]), 200

# ---------------------- REAGENDAR EXAME (paciente pode mudar data) ----------------------
@pacientes_bp.route("/exames/<int:id>", methods=["PUT"])
@jwt_required()
@role_required("paciente", "admin")
def reagendar_exame(id):
    """
    Permite ao paciente ou admin reagendar um exame já agendado.
    Apenas a data do exame pode ser alterada.
    """
    e = Exame.query.get_or_404(id) # busca exame pelo ID ou retorna 404
    dados = request.get_json() or {}

    # Verifica se o exame está agendado
    if e.status != "Agendado":
        return jsonify({"msg": "Somente exames agendados podem ser reagendados"}), 400
    
    # Atualiza a data do exame
    e.data = dados.get("data", e.data)  # paciente só pode trocar a data
    db.session.commit()
    return jsonify({"msg": "Exame reagendado", "nova_data": e.data}), 200


# ---------------------- HISTORICO DE EXAMES ----------------------
@pacientes_bp.route("/exames/historico/<int:paciente_id>", methods=["GET"])
@jwt_required()
@role_required("paciente", "admin")
def historico_exames(paciente_id):
    """
    Retorna todos os exames de um paciente específico.
    """
    exames = Exame.query.filter_by(paciente_id=paciente_id).all()
    return jsonify([{
        "id": e.id,
        "nome": e.nome,
        "data": e.data,
        "status": e.status
    } for e in exames]), 200

# ---------------------- NOTIFICAÇÕES ----------------------
@pacientes_bp.route("/notificacoes/<int:paciente_id>", methods=["GET"])
@jwt_required()
@role_required("paciente","admin")
def listar_notificacoes(paciente_id):
    """
    Retorna todas as notificações de um paciente.
    """
    notificacoes = Notificacao.query.filter_by(paciente_id=paciente_id).all()
    return jsonify([{
        "id": n.id,
        "titulo": n.titulo,
        "mensagem": n.mensagem,
        "lida": n.lida,
        "criado_em": n.criado_em
    } for n in notificacoes]), 200

# ---------------------- NOTIFICAÇÃO COMO LIDA ----------------------
@pacientes_bp.route("/notificacoes/<int:id>/ler", methods=["PUT"])
@jwt_required()
@role_required("paciente","admin")
def marcar_notificacao_lida(id):
    """
    Marca uma notificação como lida.
    """
    n = Notificacao.query.get_or_404(id)
    n.lida = True
    db.session.commit()
    return jsonify({"msg": "Notificação marcada como lida"}), 200


# ---------------------- TELECONSULTA ----------------------
@pacientes_bp.route("/teleconsulta/<int:consulta_id>", methods=["GET"])
@jwt_required()
@role_required("paciente","admin")
def acessar_teleconsulta(consulta_id):
    """
    Permite ao paciente ou admin acessar o link de teleconsulta.
    Retorna erro se a consulta não for teleconsulta.
    """
    consulta = Consulta.query.get_or_404(consulta_id)
    if not consulta.teleconsulta or not consulta.link_video:
        return jsonify({"msg": "Esta consulta não é teleconsulta"}), 400
    return jsonify({
        "msg": "Acesse sua teleconsulta",
        "link_video": consulta.link_video
    }), 200
