# Agenda & Horario model - RU 4493981
from extensions import db
from datetime import datetime

# Modelo que representa a agenda de um profissional
class Agenda(db.Model):
    __tablename__ = "agendas"
    id = db.Column(db.Integer, primary_key=True)
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissionais.id"), nullable=False) # criador da agenda
    data = db.Column(db.Date, nullable=False)

    # Restrição: um profissional só pode ter UMA agenda por data
    __table_args__ = (db.UniqueConstraint("profissional_id", "data", name="uix_profissional_data"),)

    # Relacionamento: uma agenda tem vários horários
    horarios = db.relationship("Horario", backref="agenda", cascade="all, delete-orphan", lazy=True)

# Modelo que representa os horários de atendimento em uma agenda
class Horario(db.Model):
    __tablename__ = "horarios"
    id = db.Column(db.Integer, primary_key=True)
    agenda_id = db.Column(db.Integer, db.ForeignKey("agendas.id"), nullable=False) #referencia a agenda à qual o horário pertence
    hora = db.Column(db.Time, nullable=False)
    disponivel = db.Column(db.Boolean, default=True)

    # Restrição: não permitir 2 horários iguais na mesma agenda
    __table_args__ = (db.UniqueConstraint("agenda_id", "hora", name="uix_agenda_hora"),)

