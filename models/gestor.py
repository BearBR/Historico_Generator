from extensions import db

class Gestor(db.Model):
    __tablename__ = 'gestores'
    
    id = db.Column(db.Integer, primary_key=True)
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    cargo = db.Column(db.String(100), nullable=False)  # Diretor, Vice-Diretor, Secretário
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date)
    ativo = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Gestor {self.nome} - {self.cargo}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'escola_id': self.escola_id,
            'nome': self.nome,
            'cargo': self.cargo,
            'data_inicio': self.data_inicio.strftime('%d/%m/%Y') if self.data_inicio else None,
            'data_fim': self.data_fim.strftime('%d/%m/%Y') if self.data_fim else None,
            'ativo': self.ativo
        }
