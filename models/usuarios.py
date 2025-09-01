# Usuario model - RU 4493981
from extensions import db

# Modelo que representa um usuário do sistema (paciente, profissional ou administrador)
class Usuario(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False) # Email do usuário, deve ser único para login
    senha = db.Column(db.String(255), nullable=False) # Senha do usuário, armazenada de forma segura (hash)
    role = db.Column(db.String(20), nullable=False, default="paciente")  # admin, profissional, paciente

    # Representação do objeto para debug ou logs
    def __repr__(self):
        return f"<Usuario {self.id} {self.email} {self.role}>"
