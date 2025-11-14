import os
from datetime import timedelta

class Config:
    """Configurações da aplicação"""
    
    # Chave secreta para sessões
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuração do banco de dados
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(BASE_DIR, "database", "historicos_escolares.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de upload (caso precise no futuro)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    
    # Configurações de sessão
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Configurações do PDF
    PDF_LOGO_PATH = os.path.join(BASE_DIR, 'static', 'img', 'logo_rs.png')
