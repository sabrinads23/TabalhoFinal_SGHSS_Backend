# Notificacoes model - RU 4493981
from extensions import db
from datetime import datetime

# Modelo que representa notificações enviadas aos pacientes
class Notificacao(db.Model):
    __tablename__ = "notificacoes"
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey("pacientes.id"), nullable=True)# Chave estrangeira para paciente; pode ser nula para notificações gerais
    titulo = db.Column(db.String(120), nullable=False) # Título ou assunto da notificação
    mensagem = db.Column(db.Text, nullable=False) # Conteúdo da notificação
    lida = db.Column(db.Boolean, default=False) # Indica se a notificação foi lida pelo paciente (True) ou não (False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) # Data e hora em que a notificação foi criada
