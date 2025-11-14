from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Gestor, Escola
from extensions import db
from datetime import datetime

bp = Blueprint('gestores', __name__, url_prefix='/gestores')

@bp.route('/')
def listar():
    """Lista todos os gestores"""
    gestores = Gestor.query.filter_by(ativo=True).all()
    return render_template('gestores/listar.html', gestores=gestores)

@bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    """Cadastra um novo gestor"""
    if request.method == 'POST':
        try:
            data_inicio_str = request.form['data_inicio']
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            
            data_fim = None
            if request.form.get('data_fim'):
                data_fim_str = request.form['data_fim']
                data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            
            gestor = Gestor(
                escola_id=request.form['escola_id'],
                nome=request.form['nome'],
                cargo=request.form['cargo'],
                data_inicio=data_inicio,
                data_fim=data_fim
            )
            db.session.add(gestor)
            db.session.commit()
            flash('Gestor cadastrado com sucesso!', 'success')
            return redirect(url_for('gestores.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar gestor: {str(e)}', 'danger')
    
    escolas = Escola.query.filter_by(ativa=True).all()
    return render_template('gestores/cadastrar.html', escolas=escolas)
