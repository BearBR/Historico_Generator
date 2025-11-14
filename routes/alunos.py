from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import Aluno
from extensions import db
from datetime import datetime

bp = Blueprint('alunos', __name__, url_prefix='/alunos')

@bp.route('/')
def listar():
    """Lista todos os alunos"""
    alunos = Aluno.query.filter_by(ativo=True).all()
    return render_template('alunos/listar.html', alunos=alunos)

@bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    """Cadastra um novo aluno"""
    if request.method == 'POST':
        try:
            # Converter data de nascimento
            data_nasc_str = request.form['data_nascimento']
            data_nascimento = datetime.strptime(data_nasc_str, '%Y-%m-%d').date()
            
            aluno = Aluno(
                nome_completo=request.form['nome_completo'],
                data_nascimento=data_nascimento,
                naturalidade=request.form.get('naturalidade'),
                uf_nascimento=request.form.get('uf_nascimento'),
                cpf=request.form.get('cpf'),
                rg=request.form.get('rg'),
                orgao_emissor=request.form.get('orgao_emissor'),
                uf_rg=request.form.get('uf_rg'),
                nome_mae=request.form.get('nome_mae'),
                nome_pai=request.form.get('nome_pai'),
                endereco=request.form.get('endereco'),
                municipio=request.form.get('municipio'),
                estado=request.form.get('estado'),
                cep=request.form.get('cep'),
                telefone=request.form.get('telefone'),
                email=request.form.get('email')
            )
            db.session.add(aluno)
            db.session.commit()
            flash('Aluno cadastrado com sucesso!', 'success')
            return redirect(url_for('alunos.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar aluno: {str(e)}', 'danger')
    
    return render_template('alunos/cadastrar.html')

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """Edita um aluno existente"""
    aluno = Aluno.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            data_nasc_str = request.form['data_nascimento']
            data_nascimento = datetime.strptime(data_nasc_str, '%Y-%m-%d').date()
            
            aluno.nome_completo = request.form['nome_completo']
            aluno.data_nascimento = data_nascimento
            aluno.naturalidade = request.form.get('naturalidade')
            aluno.uf_nascimento = request.form.get('uf_nascimento')
            aluno.cpf = request.form.get('cpf')
            aluno.rg = request.form.get('rg')
            aluno.orgao_emissor = request.form.get('orgao_emissor')
            aluno.uf_rg = request.form.get('uf_rg')
            aluno.nome_mae = request.form.get('nome_mae')
            aluno.nome_pai = request.form.get('nome_pai')
            aluno.endereco = request.form.get('endereco')
            aluno.municipio = request.form.get('municipio')
            aluno.estado = request.form.get('estado')
            aluno.cep = request.form.get('cep')
            aluno.telefone = request.form.get('telefone')
            aluno.email = request.form.get('email')
            
            db.session.commit()
            flash('Aluno atualizado com sucesso!', 'success')
            return redirect(url_for('alunos.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar aluno: {str(e)}', 'danger')
    
    return render_template('alunos/editar.html', aluno=aluno)

@bp.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    """Desativa um aluno"""
    try:
        aluno = Aluno.query.get_or_404(id)
        aluno.ativo = False
        db.session.commit()
        flash('Aluno desativado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao desativar aluno: {str(e)}', 'danger')
    
    return redirect(url_for('alunos.listar'))
