from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from extensions import db
from models.disciplina import AmparoLegal

bp = Blueprint('amparos_legais', __name__, url_prefix='/amparos-legais')

@bp.route('/')
def listar():
    """Lista todos os amparos legais"""
    amparos = AmparoLegal.query.order_by(AmparoLegal.ano_inicio.desc()).all()
    return render_template('amparos_legais/listar.html', amparos=amparos)

@bp.route('/novo', methods=['GET', 'POST'])
def cadastrar():
    """Cadastra novo amparo legal"""
    if request.method == 'POST':
        try:
            amparo = AmparoLegal(
                tipo=request.form['tipo'],
                numero=request.form['numero'],
                data=request.form.get('data'),
                descricao=request.form['descricao'],
                ano_inicio=int(request.form['ano_inicio']),
                ano_fim=int(request.form['ano_fim']) if request.form.get('ano_fim') else None
            )
            
            db.session.add(amparo)
            db.session.commit()
            
            flash('Amparo legal cadastrado com sucesso!', 'success')
            return redirect(url_for('amparos_legais.listar'))
        except Exception as e:
            flash(f'Erro ao cadastrar amparo legal: {str(e)}', 'danger')
    
    return render_template('amparos_legais/cadastrar.html')

@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def editar(id):
    """Edita amparo legal existente"""
    amparo = AmparoLegal.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            amparo.tipo = request.form['tipo']
            amparo.numero = request.form['numero']
            amparo.data = request.form.get('data')
            amparo.descricao = request.form['descricao']
            amparo.ano_inicio = int(request.form['ano_inicio'])
            amparo.ano_fim = int(request.form['ano_fim']) if request.form.get('ano_fim') else None
            
            db.session.commit()
            flash('Amparo legal atualizado com sucesso!', 'success')
            return redirect(url_for('amparos_legais.listar'))
        except Exception as e:
            flash(f'Erro ao atualizar amparo legal: {str(e)}', 'danger')
    
    return render_template('amparos_legais/editar.html', amparo=amparo)

@bp.route('/<int:id>/excluir', methods=['POST'])
def excluir(id):
    """Exclui amparo legal"""
    try:
        amparo = AmparoLegal.query.get_or_404(id)
        db.session.delete(amparo)
        db.session.commit()
        flash('Amparo legal excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir amparo legal: {str(e)}', 'danger')
    
    return redirect(url_for('amparos_legais.listar'))

@bp.route('/buscar')
def buscar():
    """Busca amparo legal por ano e modalidade (API para uso no histórico)"""
    ano = request.args.get('ano', type=int)
    modalidade = request.args.get('modalidade', 'Regular')
    
    if not ano:
        return jsonify({'error': 'Ano é obrigatório'}), 400
    
    # Buscar amparos que se aplicam ao ano informado
    amparos = AmparoLegal.query.filter(
        AmparoLegal.ano_inicio <= ano
    ).filter(
        db.or_(AmparoLegal.ano_fim.is_(None), AmparoLegal.ano_fim >= ano)
    ).order_by(AmparoLegal.ano_inicio.desc()).all()
    
    # Filtrar por palavras-chave relacionadas à modalidade
    if modalidade == 'EJA':
        amparos = [a for a in amparos if 'EJA' in a.numero or 'Jovens' in a.descricao]
    elif modalidade == 'Supletivo':
        amparos = [a for a in amparos if 'Supletivo' in a.descricao or '699/72' in a.numero]
    
    # Se não encontrou específico, usar LDB da época
    if not amparos:
        if ano <= 1971:
            amparos = AmparoLegal.query.filter_by(numero='4024/61').all()
        elif ano <= 1996:
            amparos = AmparoLegal.query.filter_by(numero='5692/71').all()
        else:
            amparos = AmparoLegal.query.filter_by(numero='9394/96').all()
    
    return jsonify({
        'amparos': [a.to_dict() for a in amparos]
    })
