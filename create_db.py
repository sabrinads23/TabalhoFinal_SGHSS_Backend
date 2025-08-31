from extensions import db
from app import app

# Importa todos os modelos para garantir que o SQLAlchemy crie as tabelas correspondentes
from models.usuarios import Usuario
from models.agendas import Agenda, Consulta
from models.pacientes import Paciente
from models.administracao import Leito, Internacao, Profissional, RelatorioFinanceiro, Suprimento

# Cria um contexto de aplicação para permitir operações com o banco
with app.app_context():
    # Cria todas as tabelas definidas pelos modelos importados
    db.create_all()
    
    # Mensagem de confirmação ao finalizar a criação do banco e tabelas
    print("Banco de dados e tabelas criados com sucesso!")