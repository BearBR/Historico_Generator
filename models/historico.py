from extensions import db
from datetime import datetime

class Historico(db.Model):
    __tablename__ = 'historicos'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
    
    # Informações do Histórico
    ano = db.Column(db.Integer, nullable=False)
    serie = db.Column(db.String(50), nullable=False)
    modalidade_id = db.Column(db.Integer, db.ForeignKey('modalidades_ensino.id'), nullable=False)
    nivel = db.Column(db.String(50))  # Fundamental, Médio
    
    # Datas
    data_inicio = db.Column(db.Date)
    data_termino = db.Column(db.Date)
    
    # Escola de Origem (caso seja transferência)
    escola_origem = db.Column(db.String(200))
    municipio_origem = db.Column(db.String(100))
    uf_origem = db.Column(db.String(2))
    
    # Resultado Final
    resultado_final_id = db.Column(db.Integer, db.ForeignKey('resultados_finais.id'))
    
    # Dias Letivos e Carga Horária
    dias_letivos = db.Column(db.Integer)
    carga_horaria_total = db.Column(db.Integer)
    
    # Observações
    observacoes = db.Column(db.Text)
    
    # Amparo Legal
    amparo_legal_id = db.Column(db.Integer, db.ForeignKey('amparos_legais.id'))
    
    # Conclusão de Curso
    conclusao_curso = db.Column(db.Boolean, default=False)
    data_conclusao = db.Column(db.Date)
    amparo_conclusao_id = db.Column(db.Integer, db.ForeignKey('amparos_legais.id'))
    numero_certificado = db.Column(db.String(100))
    livro_registro = db.Column(db.String(50))
    folha_registro = db.Column(db.String(50))
    observacoes_conclusao = db.Column(db.Text)
    
    # Assinaturas
    nome_diretor = db.Column(db.String(200))
    nome_secretario = db.Column(db.String(200))
    data_emissao = db.Column(db.Date)
    
    # Controle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    disciplinas = db.relationship('HistoricoDisciplina', backref='historico', lazy=True, cascade='all, delete-orphan')
    amparo_legal = db.relationship('AmparoLegal', foreign_keys=[amparo_legal_id], lazy='joined')
    amparo_conclusao = db.relationship('AmparoLegal', foreign_keys=[amparo_conclusao_id], lazy='joined')
    
    def __repr__(self):
        return f'<Historico Aluno:{self.aluno_id} Ano:{self.ano} Série:{self.serie}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'aluno_id': self.aluno_id,
            'escola_id': self.escola_id,
            'ano': self.ano,
            'serie': self.serie,
            'nivel': self.nivel,
            'data_inicio': self.data_inicio.strftime('%d/%m/%Y') if self.data_inicio else None,
            'data_termino': self.data_termino.strftime('%d/%m/%Y') if self.data_termino else None,
            'conclusao_curso': self.conclusao_curso,
            'nome_diretor': self.nome_diretor,
            'nome_secretario': self.nome_secretario
        }

class HistoricoDisciplina(db.Model):
    __tablename__ = 'historico_disciplinas'
    
    id = db.Column(db.Integer, primary_key=True)
    historico_id = db.Column(db.Integer, db.ForeignKey('historicos.id'), nullable=False)
    disciplina_historica_id = db.Column(db.Integer, db.ForeignKey('disciplinas_historicas.id'), nullable=False)
    
    # Nota Final Anual
    nota_final = db.Column(db.Float)
    
    # Frequência
    carga_horaria = db.Column(db.Integer)
    faltas = db.Column(db.Integer, default=0)
    frequencia = db.Column(db.Float)  # Nome consistente com o template
    
    # Resultado
    resultado = db.Column(db.String(10))
    
    # Relacionamento
    disciplina_historica = db.relationship('DisciplinaHistorica', backref='historicos_disciplinas')
    
    def __repr__(self):
        return f'<HistoricoDisciplina Histórico:{self.historico_id} Disciplina:{self.disciplina_historica_id}>'
    
    def calcular_frequencia(self):
        """Calcula a frequência percentual"""
        if self.carga_horaria and self.carga_horaria > 0:
            aulas_presentes = self.carga_horaria - self.faltas
            self.frequencia = round((aulas_presentes / self.carga_horaria) * 100, 2)
        return self.frequencia
    
    def to_dict(self):
        return {
            'id': self.id,
            'disciplina_historica_id': self.disciplina_historica_id,
            'nota_final': self.nota_final,
            'carga_horaria': self.carga_horaria,
            'faltas': self.faltas,
            'frequencia': self.frequencia,
            'resultado': self.resultado
        }
