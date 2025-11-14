from flask import Blueprint, render_template
from models import Escola, Aluno, Historico, Gestor

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Dashboard principal"""
    # Estatísticas básicas
    total_escolas = Escola.query.filter_by(ativa=True).count()
    total_alunos = Aluno.query.filter_by(ativo=True).count()
    total_historicos = Historico.query.count()
    total_gestores = Gestor.query.filter_by(ativo=True).count()
    
    return render_template('index.html',
                         total_escolas=total_escolas,
                         total_alunos=total_alunos,
                         total_historicos=total_historicos,
                         total_gestores=total_gestores)

@bp.route('/sobre')
def sobre():
    """Página sobre o sistema"""
    return render_template('sobre.html')
