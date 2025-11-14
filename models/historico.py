from extensions import db
from datetime import datetime

class Historico(db.Model):
    __tablename__ = 'historicos'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    
    # Informações Gerais do Histórico
    modalidade_id = db.Column(db.Integer, db.ForeignKey('modalidades_ensino.id'), nullable=False)
    nivel = db.Column(db.String(50))  # Fundamental, Médio
    
    # Escola de Origem (caso seja transferência)
    escola_origem = db.Column(db.String(200))
    municipio_origem = db.Column(db.String(100))
    uf_origem = db.Column(db.String(2))
    
    # Observações Gerais
    observacoes = db.Column(db.Text)
    
    # Amparo Legal Geral
    amparo_legal_id = db.Column(db.Integer, db.ForeignKey('amparos_legais.id'))
    
    # Conclusão de Curso
    conclusao_curso = db.Column(db.Boolean, default=False)
    data_conclusao = db.Column(db.Date)
    amparo_conclusao_id = db.Column(db.Integer, db.ForeignKey('amparos_legais.id'))
    numero_certificado = db.Column(db.String(100))
    livro_registro = db.Column(db.String(50))
    folha_registro = db.Column(db.String(50))
    observacoes_conclusao = db.Column(db.Text)
    
    # Controle de Exibição
    exibir_faltas_frequencia = db.Column(db.Boolean, default=False)
    
    # Assinaturas
    nome_diretor = db.Column(db.String(200))
    nome_secretario = db.Column(db.String(200))
    data_emissao = db.Column(db.Date)
    
    # Controle
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    anos_letivos = db.relationship('HistoricoAnoLetivo', backref='historico', lazy=True, cascade='all, delete-orphan', order_by='HistoricoAnoLetivo.ano')
    amparo_legal = db.relationship('AmparoLegal', foreign_keys=[amparo_legal_id], lazy='joined')
    amparo_conclusao = db.relationship('AmparoLegal', foreign_keys=[amparo_conclusao_id], lazy='joined')
    
    def __repr__(self):
        return f'<Historico Aluno:{self.aluno_id} Nível:{self.nivel}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'aluno_id': self.aluno_id,
            'nivel': self.nivel,
            'conclusao_curso': self.conclusao_curso,
            'nome_diretor': self.nome_diretor,
            'nome_secretario': self.nome_secretario
        }


class HistoricoAnoLetivo(db.Model):
    __tablename__ = 'historico_anos_letivos'
    
    id = db.Column(db.Integer, primary_key=True)
    historico_id = db.Column(db.Integer, db.ForeignKey('historicos.id'), nullable=False)
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
    
    # Dados do Ano Letivo
    ano = db.Column(db.Integer, nullable=False)
    serie = db.Column(db.String(50), nullable=False)
    
    # Datas
    data_inicio = db.Column(db.Date)
    data_termino = db.Column(db.Date)
    
    # Resultado Final do Ano
    resultado_final_id = db.Column(db.Integer, db.ForeignKey('resultados_finais.id'))
    
    # Dias Letivos e Carga Horária Total do Ano
    dias_letivos = db.Column(db.Integer)
    carga_horaria_total = db.Column(db.Integer)
    
    # Relacionamentos
    disciplinas = db.relationship('HistoricoAnoDisciplina', backref='ano_letivo', lazy=True, cascade='all, delete-orphan')
    escola = db.relationship('Escola', lazy='joined', overlaps="anos_letivos")
    resultado_final = db.relationship('ResultadoFinal', lazy='joined')
    
    def __repr__(self):
        return f'<HistoricoAnoLetivo Ano:{self.ano} Série:{self.serie}>'


class HistoricoAnoDisciplina(db.Model):
    __tablename__ = 'historico_ano_disciplinas'
    
    id = db.Column(db.Integer, primary_key=True)
    ano_letivo_id = db.Column(db.Integer, db.ForeignKey('historico_anos_letivos.id'), nullable=False)
    disciplina_historica_id = db.Column(db.Integer, db.ForeignKey('disciplinas_historicas.id'), nullable=False)
    
    # Nota Final Anual
    nota_final = db.Column(db.Float)
    
    # Frequência
    carga_horaria = db.Column(db.Integer)
    faltas = db.Column(db.Integer, default=0)
    frequencia = db.Column(db.Float)
    
    # Resultado
    resultado = db.Column(db.String(10))
    
    # Relacionamento
    disciplina_historica = db.relationship('DisciplinaHistorica', backref='historicos_ano_disciplinas')
    
    def __repr__(self):
        return f'<HistoricoAnoDisciplina AnoLetivo:{self.ano_letivo_id} Disciplina:{self.disciplina_historica_id}>'
    
    def calcular_frequencia(self):
        """Calcula a frequência percentual"""
        if self.carga_horaria and self.carga_horaria > 0:
            aulas_presentes = self.carga_horaria - self.faltas
            self.frequencia = round((aulas_presentes / self.carga_horaria) * 100, 2)
        return self.frequencia


# Manter compatibilidade com código existente
HistoricoDisciplina = HistoricoAnoDisciplina
