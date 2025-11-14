from flask import Blueprint, render_template, request, redirect, url_for, flash
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
