# Paciente model - RU 4493981
from extensions import db
from datetime import date

# Modelo que representa um paciente do hospital
class Paciente(db.Model):
    __tablename__ = "pacientes"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True) # Chave estrangeira opcional que vincula o paciente a um usuário do sistema
    nome = db.Column(db.String(120), nullable=False)
    cpf = db.Column(db.String(11), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    senha = db.Column(db.String(255), nullable=False) 
    

