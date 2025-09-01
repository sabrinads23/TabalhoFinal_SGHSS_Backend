# Exames model - RU 4493981
from extensions import db
from datetime import datetime

# Modelo que representa um exame médico de um paciente
class Exame(db.Model):
    __tablename__ = "exames"
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False) #referencia o paciente que realizará o exame
    nome = db.Column(db.String(120), nullable=False) # Nome do exame (ex: "Hemograma", "Raio-X")
    data = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) #padrão é o momento da criação
    status = db.Column(db.String(20), default="agendado")  # agendado, realizado, cancelado, reagendado
