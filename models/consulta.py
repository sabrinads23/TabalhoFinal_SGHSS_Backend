# Consulta model - RU 4493981
from extensions import db
from datetime import datetime


# Modelo que representa uma consulta médica
class Consulta(db.Model):
    __tablename__ = "consultas"

    # Restrição: não permite duas consultas no mesmo horário da mesma agenda
    __table_args__ = (db.UniqueConstraint("agenda_id", "horario_id", name="uq_agenda_horario"),)

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissionais.id"), nullable=False)
    agenda_id = db.Column(db.Integer, db.ForeignKey("agendas.id"), nullable=False)
    horario_id = db.Column(db.Integer, db.ForeignKey("horarios.id"), nullable=False)

    data_consulta = db.Column(db.Date, nullable=False)
    hora_consulta = db.Column(db.Time, nullable=False)

    status = db.Column(db.String(20), nullable=False, default="agendada") # agendada, realizada, cancelada 
    teleconsulta = db.Column(db.Boolean, default=False) # Indica se a consulta é online (True) ou presencial (False)
    link_video = db.Column(db.String(255), nullable=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relações
    paciente = db.relationship("Paciente", backref="consultas")
    profissional = db.relationship("Profissional", backref="consultas")
    agenda = db.relationship("Agenda", backref="consultas")
    horario = db.relationship("Horario", backref="consulta", uselist=False)
