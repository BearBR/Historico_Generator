# Models package
from models.escola import Escola
from models.aluno import Aluno
from models.disciplina import DisciplinaHistorica, ModalidadeEnsino, AmparoLegal, ResultadoFinal
from models.historico import Historico, HistoricoDisciplina
from models.gestor import Gestor

__all__ = [
    'Escola',
    'Aluno',
    'DisciplinaHistorica',
    'ModalidadeEnsino',
    'AmparoLegal',
    'ResultadoFinal',
    'Historico',
    'HistoricoDisciplina',
    'Gestor'
]
