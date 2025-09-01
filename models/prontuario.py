# Prontuario & Receita model - RU 4493981
from extensions import db
from datetime import datetime

# Modelo que representa o prontuário médico de um paciente
class Prontuario(db.Model):
    __tablename__ = "prontuarios"
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False) # Referência ao paciente dono do prontuário
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissionais.id"), nullable=False) # Referência ao profissional que registrou o prontuário
    data_registro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # padrão é o momento da criação
    descricao = db.Column(db.Text, nullable=False) # Descrição do prontuário (observações, histórico clínico, evolução do paciente)

# Modelo que representa uma receita médica
class Receita(db.Model):
    __tablename__ = "receitas"
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False) # Referência ao paciente que receberá a receita
    profissional_id = db.Column(db.Integer, db.ForeignKey("profissionais.id"), nullable=False) # Referência ao profissional que emitiu a receita
    data_emissao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) # Data e hora de emissão da receita
    conteudo = db.Column(db.Text, nullable=False) # Conteúdo da receita (medicações, doses, instruções) 
    assinatura_digital = db.Column(db.String(255), nullable=True) # Assinatura digital do profissional, se aplicável
