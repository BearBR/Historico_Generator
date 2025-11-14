from extensions import db
from datetime import datetime

class Aluno(db.Model):
    __tablename__ = 'alunos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(200), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    naturalidade = db.Column(db.String(100))
    uf_nascimento = db.Column(db.String(2))
    cpf = db.Column(db.String(14), unique=True)
    rg = db.Column(db.String(20))
    orgao_emissor = db.Column(db.String(20))
    uf_rg = db.Column(db.String(2))
    
    # Filiação
    nome_mae = db.Column(db.String(200))
    nome_pai = db.Column(db.String(200))
    
    # Endereço
    endereco = db.Column(db.String(200))
    municipio = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    
    # Controle
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    historicos = db.relationship('Historico', backref='aluno', lazy=True)
    
    def __repr__(self):
        return f'<Aluno {self.nome_completo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'data_nascimento': self.data_nascimento.strftime('%d/%m/%Y') if self.data_nascimento else None,
            'cpf': self.cpf,
            'rg': self.rg,
            'ativo': self.ativo
        }
