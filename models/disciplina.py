from extensions import db

class DisciplinaHistorica(db.Model):
    __tablename__ = 'disciplinas_historicas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    codigo = db.Column(db.String(20))
    ano_inicio = db.Column(db.Integer, nullable=False)
    ano_fim = db.Column(db.Integer)
    carga_horaria_padrao = db.Column(db.Integer)
    serie = db.Column(db.String(50))
    modalidade_id = db.Column(db.Integer, db.ForeignKey('modalidades_ensino.id'))
    ativa = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Disciplina {self.nome} ({self.ano_inicio}-{self.ano_fim or "atual"})>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'codigo': self.codigo,
            'ano_inicio': self.ano_inicio,
            'ano_fim': self.ano_fim,
            'carga_horaria_padrao': self.carga_horaria_padrao,
            'ativa': self.ativa
        }

class ModalidadeEnsino(db.Model):
    __tablename__ = 'modalidades_ensino'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    descricao = db.Column(db.String(200))
    ano_inicio = db.Column(db.Integer)
    ano_fim = db.Column(db.Integer)
    ativa = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    disciplinas = db.relationship('DisciplinaHistorica', backref='modalidade', lazy=True)
    historicos = db.relationship('Historico', backref='modalidade', lazy=True)
    
    def __repr__(self):
        return f'<Modalidade {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'ativa': self.ativa
        }

class AmparoLegal(db.Model):
    __tablename__ = 'amparos_legais'
    
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    numero = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date)
    descricao = db.Column(db.String(500))
    ano_inicio = db.Column(db.Integer)
    ano_fim = db.Column(db.Integer)
    ativo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Amparo {self.tipo} {self.numero}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'numero': self.numero,
            'descricao': self.descricao,
            'ativo': self.ativo
        }

class ResultadoFinal(db.Model):
    __tablename__ = 'resultados_finais'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(10), nullable=False, unique=True)
    descricao = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50))
    ano_inicio = db.Column(db.Integer)
    ano_fim = db.Column(db.Integer)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    historicos = db.relationship('Historico', backref='resultado_final', lazy=True)
    
    def __repr__(self):
        return f'<Resultado {self.codigo} - {self.descricao}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'descricao': self.descricao,
            'tipo': self.tipo,
            'ativo': self.ativo
        }
