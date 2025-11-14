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
            gestor = Gestor(
                escola_id=request.form['escola_id'],
                nome=request.form['nome'],
                cargo=request.form['cargo']
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

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """Edita um gestor existente"""
    gestor = Gestor.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            gestor.nome = request.form['nome']
            gestor.cargo = request.form['cargo']
            gestor.escola_id = request.form['escola_id']
            
            data_inicio_str = request.form['data_inicio']
            gestor.data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            
            if request.form.get('data_fim'):
                data_fim_str = request.form['data_fim']
                gestor.data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            else:
                gestor.data_fim = None
            
            gestor.ativo = bool(request.form.get('ativo'))
            
            db.session.commit()
            flash('Gestor atualizado com sucesso!', 'success')
            return redirect(url_for('gestores.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar gestor: {str(e)}', 'danger')
    
    escolas = Escola.query.filter_by(ativa=True).all()
    return render_template('gestores/editar.html', gestor=gestor, escolas=escolas)

@bp.route('/excluir/<int:id>', methods=['POST'])
def excluir(id):
    """Exclui (desativa) um gestor"""
    try:
        gestor = Gestor.query.get_or_404(id)
        nome_gestor = gestor.nome
        
        # Apenas desativar ao invés de deletar
        gestor.ativo = False
        db.session.commit()
        
        flash(f'Gestor {nome_gestor} excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir gestor: {str(e)}', 'danger')
    
    return redirect(url_for('gestores.listar'))

