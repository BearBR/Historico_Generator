from extensions import db
from datetime import datetime

class Escola(db.Model):
    __tablename__ = 'escolas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    endereco = db.Column(db.String(200), nullable=False)
    municipio = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False, default='RS')
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    
    # Decretos e Documentos
    decreto_criacao = db.Column(db.String(50))
    data_criacao = db.Column(db.Date)
    doe_criacao = db.Column(db.Date)
    
    decreto_reorganizacao = db.Column(db.String(50))
    data_reorganizacao = db.Column(db.Date)
    doe_reorganizacao = db.Column(db.Date)
    
    parecer_alteracao = db.Column(db.String(50))
    data_alteracao = db.Column(db.Date)
    doe_alteracao = db.Column(db.Date)
    
    # Informações Administrativas
    entidade_mantenedora = db.Column(db.String(200))
    cre = db.Column(db.String(20))  # Coordenadoria Regional de Educação
    sede_cre = db.Column(db.String(100))
    idt = db.Column(db.String(20))  # Identificador da escola
    
    # Logo da Escola
    logo = db.Column(db.String(255))  # Caminho da imagem
    
    # Controle
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    anos_letivos = db.relationship('HistoricoAnoLetivo', foreign_keys='HistoricoAnoLetivo.escola_id', lazy=True)
    gestores = db.relationship('Gestor', backref='escola', lazy=True)
    
    def __repr__(self):
        return f'<Escola {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'endereco': self.endereco,
            'municipio': self.municipio,
            'estado': self.estado,
            'telefone': self.telefone,
            'idt': self.idt,
            'ativa': self.ativa
        }
