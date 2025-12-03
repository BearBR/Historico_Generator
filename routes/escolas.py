from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import Escola, Gestor
from extensions import db
from werkzeug.utils import secure_filename
from datetime import datetime
import os

bp = Blueprint('escolas', __name__, url_prefix='/escolas')

# Configurações de upload
UPLOAD_FOLDER = 'static/uploads/logos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/')
def listar():
    """Lista todas as escolas"""
    escolas = Escola.query.filter_by(ativa=True).all()
    return render_template('escolas/listar.html', escolas=escolas)

@bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    """Cadastra uma nova escola"""
    if request.method == 'POST':
        try:
            # Processar upload da logo
            logo_filename = None
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Criar nome único
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    logo_filename = f"{timestamp}_{filename}"
                    
                    # Criar diretório se não existir
                    upload_path = os.path.join('static', 'uploads', 'logos')
                    os.makedirs(upload_path, exist_ok=True)
                    
                    # Salvar arquivo
                    file.save(os.path.join(upload_path, logo_filename))
            
            escola = Escola(
                nome=request.form['nome'],
                endereco=request.form['endereco'],
                municipio=request.form['municipio'],
                estado=request.form.get('estado', 'RS'),
                telefone=request.form.get('telefone'),
                email=request.form.get('email'),
                idt=request.form.get('idt'),
                entidade_mantenedora=request.form.get('entidade_mantenedora'),
                logo=logo_filename
            )
            db.session.add(escola)
            db.session.commit()
            flash('Escola cadastrada com sucesso!', 'success')
            return redirect(url_for('escolas.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar escola: {str(e)}', 'danger')
    
    return render_template('escolas/cadastrar.html')

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """Edita uma escola existente"""
    escola = Escola.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Processar upload da logo
            if 'logo' in request.files:
                file = request.files['logo']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    logo_filename = f"{timestamp}_{filename}"
                    
                    upload_path = os.path.join('static', 'uploads', 'logos')
                    os.makedirs(upload_path, exist_ok=True)
                    
                    file.save(os.path.join(upload_path, logo_filename))
                    escola.logo = logo_filename
            
            escola.nome = request.form['nome']
            escola.endereco = request.form['endereco']
            escola.municipio = request.form['municipio']
            escola.estado = request.form.get('estado', 'RS')
            escola.telefone = request.form.get('telefone')
            escola.email = request.form.get('email')
            escola.idt = request.form.get('idt')
            escola.entidade_mantenedora = request.form.get('entidade_mantenedora')
            
            db.session.commit()
            flash('Escola atualizada com sucesso!', 'success')
            return redirect(url_for('escolas.listar'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar escola: {str(e)}', 'danger')
    
    return render_template('escolas/editar.html', escola=escola)

@bp.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    """Desativa uma escola"""
    try:
        escola = Escola.query.get_or_404(id)
        escola.ativa = False
        db.session.commit()
        flash('Escola desativada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao desativar escola: {str(e)}', 'danger')
    
    return redirect(url_for('escolas.listar'))

@bp.route('/cadastrar_rapido', methods=['POST'])
def cadastrar_rapido():
    """Cadastra uma escola rapidamente via AJAX (apenas nome)"""
    try:
        data = request.get_json()
        nome = data.get('nome', '').strip()
        
        if not nome:
            return jsonify({'success': False, 'message': 'Nome da escola é obrigatório'}), 400
        
        # Verificar se já existe
        escola_existente = Escola.query.filter_by(nome=nome, ativa=True).first()
        if escola_existente:
            return jsonify({
                'success': True, 
                'message': 'Escola já existe no sistema',
                'escola_id': escola_existente.id
            })
        
        # Criar nova escola com dados mínimos
        escola = Escola(
            nome=nome,
            endereco=data.get('endereco', 'Não informado'),
            municipio=data.get('municipio', 'Não informado'),
            estado=data.get('estado', 'RS')
        )
        
        db.session.add(escola)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Escola cadastrada com sucesso',
            'escola_id': escola.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@bp.route('/<int:id>/set-padrao', methods=['POST'])
def set_padrao(id):
    """Marca uma escola como padrão (escola emissora de históricos)"""
    try:
        escola = Escola.query.get(id)
        
        if not escola:
            return jsonify({'error': 'Escola não encontrada'}), 404
        
        # Se já é padrão, desmarcar
        if escola.eh_escola_padrao:
            escola.eh_escola_padrao = False
            mensagem = f"❌ {escola.nome} desmarcada como escola padrão"
        else:
            # Desmarcar todas as outras escolas
            Escola.query.update({Escola.eh_escola_padrao: False})
            
            # Marcar esta como padrão
            escola.eh_escola_padrao = True
            mensagem = f"✅ {escola.nome} marcada como escola padrão dos históricos"
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': mensagem,
            'eh_padrao': escola.eh_escola_padrao
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
