# Profissionais routes - RU 4493981
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity, get_jwt
from werkzeug.security import check_password_hash
from extensions import db
from models.profissionais import Profissional
from .decorators import role_required
from models.agendas import Agenda, Horario
from models.consulta import Consulta
from models.prontuario import Prontuario, Receita
from models.pacientes import Paciente
from sqlalchemy import text, func, select  
from datetime import datetime

# Cria um blueprint para rotas de profissionais
profissionais_bp = Blueprint("profissionais", __name__, url_prefix="/profissionais")

# ---------------------- LOGIN PROFISSIONAIS ----------------------
@profissionais_bp.route("/login", methods=["POST"])
def login_profissional():
    """
    Permite ao profissional fazer login usando CRM e senha.
    Retorna token JWT e dados do profissional.
    """
    dados = request.get_json() or {}
    crm = dados.get("crm")
    senha = dados.get("senha")

    # Se campos não preenchidos
    if not crm or not senha:
        return jsonify({"msg": "CRM e senha são obrigatórios"}), 400

    profissional = Profissional.query.filter_by(crm=crm).first()
    
    # Se campos preenchidos incorretamente
    if not profissional or not check_password_hash(profissional.senha, senha):
        return jsonify({"msg": "Credenciais inválidas"}), 401

    # Gera o token JWT
    token = create_access_token(
        identity=str(profissional.id),
        additional_claims={
            "role": "profissional",
            "tipo": profissional.tipo
        }
    )

    # Retorna token e dados do usuário
    return jsonify({
        "access_token": token,
        "profissional_id": profissional.id,
        "nome": profissional.nome,
        "tipo": profissional.tipo,
        "crm": profissional.crm
    }), 200

# ---------------------- CRIAR AGENDA (somente MÉDICO) ----------------------
@profissionais_bp.route("/agendas", methods=["POST"])
@jwt_required()
def criar_agenda():
    """
    Permite ao médico criar uma agenda para um dia específico.
    Verifica se já existe agenda para o mesmo dia.
    """
    user_id = get_jwt_identity()   # ID do profissional (vem como string)
    claims = get_jwt()             # role, tipo, etc.

    # Verifica o tipo do usuário
    if claims.get("tipo") != "medico":
        return jsonify({"msg": "Apenas médicos podem criar agenda"}), 403

    dados = request.get_json() or {}
    data_str = dados.get("data")

    # Se campo data não for preenchido
    if not data_str:
        return jsonify({"msg": "O campo 'data' é obrigatório (formato YYYY-MM-DD)"}), 400

    try:
        # Converte a string para objeto date
        data_convertida = datetime.strptime(data_str, "%Y-%m-%d").date()
    except Exception:
        return jsonify({"msg": "Formato de data inválido. Use YYYY-MM-DD"}), 400

    # Verifica se já existe agenda desse médico nesse dia
    agenda_existente = Agenda.query.filter_by(
        profissional_id=int(user_id), data=data_convertida).first()

    if agenda_existente:
        return jsonify({
            "msg": "Já existe uma agenda cadastrada para este profissional nesta data",
            "agenda_id": agenda_existente.id,
            "data": str(agenda_existente.data)
        }), 400
    
    # Criação da agenda
    a = Agenda(profissional_id=int(user_id), data=data_convertida)
    db.session.add(a)
    db.session.commit()

    return jsonify({
        "msg": "Agenda criada com sucesso",
        "agenda_id": a.id,
        "data": str(a.data)  # aqui volta como string pro JSON
    }), 201


# ---------------------- DISPONIBILIZAR HORÁRIOS ----------------------
@profissionais_bp.route("/agendas/<int:agenda_id>/horarios", methods=["POST"])
@jwt_required()
def disponibilizar_horarios(agenda_id):
    """
    Permite ao médico disponibilizar horários para uma agenda existente.
    Valida horários duplicados e formata corretamente.
    """
    user_id = get_jwt_identity()
    claims = get_jwt()

    # Verifica o tipo do usuário
    if claims.get("tipo") != "medico":
        return jsonify({"msg": "Apenas médicos podem disponibilizar horários"}), 403

    # Tratamento de erro para agenda inexistente
    agenda = Agenda.query.get(agenda_id)
    if not agenda:
        return jsonify({"msg": "Agenda inválida ou não encontrada"}), 404

    if agenda.profissional_id != int(user_id):
        return jsonify({"msg": "Agenda não pertence a este médico"}), 403

    dados = request.get_json() or {}
    horarios = dados.get("horarios", [])
    criados = []
    ignorados = []

    for h in horarios:
        try:
            # Converter string para objeto time
            hora_convertida = datetime.strptime(h, "%H:%M").time()
        except Exception:
            return jsonify({"msg": f"Formato de hora inválido: {h}. Use HH:MM"}), 400

        # Verificar se já existe esse horário na agenda
        existe = Horario.query.filter_by(
            agenda_id=agenda_id,
            hora=hora_convertida
        ).first()

        if existe:
            ignorados.append(h)
            continue

        horario = Horario(
            agenda_id=agenda_id,
            hora=hora_convertida,
            disponivel=True
        )
        db.session.add(horario)
        criados.append(hora_convertida.strftime("%H:%M"))

    db.session.commit()

    return jsonify({
        "msg": (
            "Alguns horários já existiam e foram ignorados."
            if ignorados else
            "Todos os horários foram cadastrados com sucesso."
        ),
        "horarios_criados": criados,
        "horarios_ignorados": ignorados
    }), 201

# ---------------------- LISTAR AGENDAS (médico autenticado) ----------------------
@profissionais_bp.route("/agendas", methods=["GET"])
@jwt_required()
def listar_agendas():
    """
    Lista todas as agendas do médico logado.
    Pode filtrar por data usando query param 'data'.
    """
    user_id = get_jwt_identity()
    claims = get_jwt()

    # Verifica o tipo do usuário
    if claims.get("tipo") != "medico":
        return jsonify({"msg": "Apenas médicos podem listar agendas"}), 403

    data_str = request.args.get("data")  # opcional: YYYY-MM-DD
    query = Agenda.query.filter_by(profissional_id=int(user_id))

    if data_str:
        try:
            data_convertida = datetime.strptime(data_str, "%Y-%m-%d").date()
        except Exception:
            return jsonify({"msg": "Formato de data inválido. Use YYYY-MM-DD"}), 400
        query = query.filter_by(data=data_convertida)

    agendas = query.order_by(Agenda.data.asc()).all()

    return jsonify([
        {
            "agenda_id": a.id,
            "data": str(a.data)
        }
        for a in agendas
    ]), 200


# ---------------------- APAGAR AGENDA ----------------------
@profissionais_bp.route("/agendas/<int:agenda_id>", methods=["DELETE"])
@jwt_required()
def apagar_agenda(agenda_id):
    """
    Permite ao médico apagar uma agenda.
    Antes de apagar, verifica se existem consultas ocupadas.
    Também remove horários vinculados à agenda.
    """
    user_id = get_jwt_identity()
    claims = get_jwt()

    # Verifica o tipo do usuário
    if claims.get("tipo") != "medico":
        return jsonify({"msg": "Apenas médicos podem apagar agendas"}), 403

    agenda = Agenda.query.get_or_404(agenda_id)
    if agenda.profissional_id != int(user_id):
        return jsonify({"msg": "Agenda não pertence a este médico"}), 403

    # Verificação de consultas ocupadas
    cols = set()
    try:
        res = db.session.execute(text("PRAGMA table_info(consultas)"))
        cols = {row[1] for row in res}  # row[1] = name
    except Exception:
        pass

    # Monta filtros disponíveis sem referenciar colunas que não existem
    where_parts = []
    params = {}

    # status ≠ 'disponivel' para bloquear exclusão
    if "status" in cols:
        where_parts.append("status != :status_disp")
        params["status_disp"] = "disponivel"

    # limitar ao profissional da agenda (se existir a coluna)
    if "profissional_id" in cols:
        where_parts.append("profissional_id = :prof_id")
        params["prof_id"] = agenda.profissional_id

    # limitar ao dia da agenda (se existir alguma coluna de data)
    if "data_consulta" in cols:
        where_parts.append("data_consulta = :dt")
        params["dt"] = str(agenda.data)
        data_col = "data_consulta"
    elif "data" in cols:
        where_parts.append("data = :dt")
        params["dt"] = str(agenda.data)
        data_col = "data"
    else:
        data_col = None  # sem filtro por data

    where_clause = " AND ".join(where_parts) if where_parts else "1=1"

    # Verifica consultas ocupadas (COUNT(*))
    sql_count = f"SELECT COUNT(*) AS c FROM consultas WHERE {where_clause}"
    try:
        ocupadas = db.session.execute(text(sql_count), params).scalar() or 0
    except Exception as e:
        # Se nem COUNT consegue (caso extremo), por segurança bloqueia
        return jsonify({"msg": "Falha ao verificar consultas vinculadas à agenda", "erro": str(e)}), 500

    if ocupadas > 0:
        return jsonify({
            "msg": "Não é possível apagar a agenda: existem consultas ocupadas vinculadas"
        }), 409

    # Apagar consultas e horários vinculados
    where_parts_del = []
    params_del = {}

    if "profissional_id" in cols:
        where_parts_del.append("profissional_id = :prof_id")
        params_del["prof_id"] = agenda.profissional_id

    if data_col:
        where_parts_del.append(f"{data_col} = :dt")
        params_del["dt"] = str(agenda.data)

    where_clause_del = " AND ".join(where_parts_del) if where_parts_del else "1=1"
    sql_del = f"DELETE FROM consultas WHERE {where_clause_del}"
    try:
        db.session.execute(text(sql_del), params_del)
    except Exception as e:
        return jsonify({"msg": "Falha ao remover consultas da agenda", "erro": str(e)}), 500

    # Apaga horários da agenda se a tabela/coluna existir
    try:
        res_h = db.session.execute(text("PRAGMA table_info(horarios)"))
        cols_h = {row[1] for row in res_h}
        if "agenda_id" in cols_h:
            db.session.execute(text("DELETE FROM horarios WHERE agenda_id = :aid"), {"aid": agenda_id})
    except Exception:
        pass  # se não existir, ignora

    # Apaga a própria agenda
    db.session.delete(agenda)
    db.session.commit()

    return jsonify({"msg": "Agenda removida com sucesso"}), 200


# ---------------------- OBTER AGENDA (detalhe + horários) ----------------------
@profissionais_bp.route("/agendas/<int:agenda_id>", methods=["GET"])
@jwt_required()
def obter_agenda(agenda_id):
    """
    Retorna detalhes de uma agenda específica, incluindo horários e consultas.
    """
    user_id = get_jwt_identity()
    claims = get_jwt()

    # Verifica o tipo do usuário
    if claims.get("tipo") != "medico":
        return jsonify({"msg": "Apenas médicos podem acessar agendas"}), 403

    agenda = Agenda.query.get_or_404(agenda_id)
    if agenda.profissional_id != int(user_id):
        return jsonify({"msg": "Agenda não pertence a este médico"}), 403

    # pega horários dessa agenda
    horarios = Horario.query.filter_by(agenda_id=agenda.id).order_by(Horario.hora.asc()).all()
    horario_ids = [h.id for h in horarios]

    # consultas atreladas aos horários
    consultas = []
    if horario_ids:
        consultas = Consulta.query.filter(Consulta.horario_id.in_(horario_ids)) \
                                  .order_by(Consulta.hora_consulta.asc()).all()

    def _fmt_hora(h):
        try:
            return h.strftime("%H:%M")
        except Exception:
            return str(h)

    return jsonify({
        "agenda_id": agenda.id,
        "data": str(agenda.data),
        "horarios": [
            {
                "horario_id": h.id,
                "hora": _fmt_hora(h.hora) if hasattr(h, "hora") else None
            } for h in horarios
        ],
        "consultas": [
            {
                "id": c.id,
                "horario_id": c.horario_id,
                "hora": _fmt_hora(c.hora_consulta),
                "status": c.status,
                "paciente_id": c.paciente_id
            } for c in consultas
        ]
    }), 200

# ---------------------- LISTAR CONSULTAS DO PROFISSIONAL ----------------------
@profissionais_bp.route("/consultas/profissional/<int:profissional_id>", methods=["GET"])
@jwt_required()
def listar_consultas_profissional(profissional_id):
    """
    Lista todas as consultas associadas a um profissional.
    """
    consultas = Consulta.query.filter_by(profissional_id=profissional_id).all()
    
    return jsonify([{
        "id": c.id,
        "paciente_id": c.paciente_id,
        "data": str(c.data_consulta),
        "hora": c.hora_consulta.strftime("%H:%M:%S") if c.hora_consulta else None,
        "status": c.status
    } for c in consultas]), 200

# ---------------------- REGISTRAR PRONTUÁRIO ----------------------
@profissionais_bp.route("/prontuarios", methods=["POST"])
@jwt_required()
@role_required("profissional", "admin")
def registrar_prontuario():
    """
    Permite ao profissional registrar um prontuário de um paciente.
    """
    user_id = get_jwt_identity()
    dados = request.get_json() or {}

    pr = Prontuario(
        paciente_id=dados["paciente_id"],
        profissional_id=int(user_id),
        descricao=dados["descricao"]
    )
    db.session.add(pr)
    db.session.commit()
    return jsonify({"msg": "Prontuário registrado", "prontuario_id": pr.id}), 201


# ---------------------- EMITIR RECEITA ----------------------
@profissionais_bp.route("/receitas", methods=["POST"])
@jwt_required()
@role_required("profissional", "admin")
def emitir_receita():
    """
    Permite ao profissional emitir uma receita para um paciente.
    """
    user_id = get_jwt_identity()
    dados = request.get_json() or {}

    r = Receita(
        paciente_id=dados["paciente_id"],
        profissional_id=int(user_id),
        conteudo=dados["conteudo"],
        assinatura_digital=dados.get("assinatura_digital")
    )
    db.session.add(r)
    db.session.commit()
    return jsonify({"msg": "Receita emitida", "receita_id": r.id}), 201


# ---------------------- HISTÓRICO DO PACIENTE ----------------------
@profissionais_bp.route("/pacientes/historico", methods=["GET"])
@jwt_required()
def historico_paciente():
    """
    Retorna histórico completo de um paciente (prontuários, receitas e consultas)
    Pode filtrar pelo nome ou ID do paciente.
    """
    nome = request.args.get("nome")
    paciente_id = request.args.get("id")

    # Se informações não preenchidas
    if paciente_id:
        paciente = Paciente.query.get(paciente_id)
    elif nome:
        paciente = Paciente.query.filter(Paciente.nome.ilike(f"%{nome}%")).first()
    else:
        return jsonify({"msg": "Informe nome ou id do paciente"}), 400

    # Se paciente não existe
    if not paciente:
        return jsonify({"msg": "Paciente não encontrado"}), 404

    prontuarios = Prontuario.query.filter_by(paciente_id=paciente.id).all()
    receitas = Receita.query.filter_by(paciente_id=paciente.id).all()
    consultas = Consulta.query.filter_by(paciente_id=paciente.id).all()

    return jsonify({
        "paciente": {"id": paciente.id, "nome": paciente.nome},
        "prontuarios": [{"id": p.id, "descricao": p.descricao} for p in prontuarios],
        "receitas": [{"id": r.id, "conteudo": r.conteudo} for r in receitas],
        "consultas": [{"id": c.id, "data": str(c.data_consulta), "hora": c.hora_consulta} for c in consultas]
    }), 200


# ---------------------- TELECONSULTA ----------------------
@profissionais_bp.route("/teleconsulta", methods=["POST"])
@jwt_required()
def iniciar_teleconsulta():
    """
    Inicia teleconsulta com um paciente específico.
    Retorna link simulado para teleconsulta.
    """
    dados = request.get_json() or {}
    paciente_id = dados.get("paciente_id")

    # Se paciente não preenchido
    if not paciente_id:
        return jsonify({"msg": "Paciente é obrigatório"}), 400

    # Se paciente não existe
    paciente = Paciente.query.get(paciente_id)
    if not paciente:
        return jsonify({"msg": "Paciente não encontrado"}), 404

    return jsonify({
        "msg": "Teleconsulta iniciada",
        "paciente": {"id": paciente.id, "nome": paciente.nome},
        "link": f"https://sghss.com/teleconsulta/{paciente.id}"
    }), 200
