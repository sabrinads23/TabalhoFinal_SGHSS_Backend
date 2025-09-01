# Administracao models - RU 4493981
from extensions import db
from datetime import datetime

# Modelo para representar os leitos do hospital
class Leito(db.Model):
    __tablename__ = "leitos"
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)
    tipo = db.Column(db.String(30), nullable=True)
    ocupado = db.Column(db.Boolean, default=False)

# Modelo para registrar as internações de pacientes
class Internacao(db.Model):
    __tablename__ = "internacoes"
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=False)
    leito_id = db.Column(db.Integer, db.ForeignKey("leitos.id"), nullable=False)
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) #padrão é o momento da criação
    data_fim = db.Column(db.DateTime, nullable=True) #pode ser nula se o paciente ainda estiver internado

# Modelo para registrar relatórios financeiros do hospital
class RelatorioFinanceiro(db.Model):
    __tablename__ = "relatorios_financeiros"
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) #padrão é o momento da criação

# Modelo para controlar suprimentos hospitalares
class Suprimento(db.Model):
    __tablename__ = "suprimentos"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    quantidade = db.Column(db.Integer, default=0, nullable=False)
    descricao = db.Column(db.String(100), nullable=True)
