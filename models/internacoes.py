# Internacoes model- RU 4493981
from extensions import db
from datetime import datetime

# Modelo que representa uma internação hospitalar
class Internacao(db.Model):
    __tablename__ = "internacoes"

    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False) # referencia o paciente internado
    leito_id = db.Column(db.Integer, db.ForeignKey("leitos.id"), nullable=False) # referencia o leito ocupado pelo paciente
    data_internacao = db.Column(db.DateTime, default=datetime.utcnow) # padrão é o momento da criação do registro
    data_alta = db.Column(db.DateTime, nullable=True) # pode ser nula se o paciente ainda estiver internado
      
