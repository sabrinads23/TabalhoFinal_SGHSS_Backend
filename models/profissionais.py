# Profissional model - RU 4493981
from extensions import db

# Modelo que representa um profissional de saúde do hospital
class Profissional(db.Model):
    __tablename__ = "profissionais"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    crm = db.Column(db.String(30), unique=True, nullable=True)
    especialidade = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)  # hashed
    tipo = db.Column(db.String(40), nullable=False, default="medico")  # medico, enfermeiro, farmaceutico, tec. enfermagem
