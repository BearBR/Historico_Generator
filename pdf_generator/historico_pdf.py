"""
Gerador de PDF para Históricos Escolares
Utiliza xhtml2pdf para renderizar HTML/CSS em PDF
"""
from flask import render_template, url_for
from xhtml2pdf import pisa
from datetime import datetime
import io
import os


def link_callback(uri, rel):
    """
    Callback para resolver caminhos de arquivos (imagens, CSS, etc)
    Necessário para xhtml2pdf processar recursos locais
    """
    # Remove o prefixo /static/ se existir
    if uri.startswith('/static/'):
        uri = uri[8:]  # Remove '/static/'
    
    # Caminho absoluto para a pasta static
    sPath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    sPath = os.path.abspath(os.path.join(sPath, uri))
    
    # Verifica se o arquivo existe
    if not os.path.isfile(sPath):
        return None  # Retorna None para ignorar imagens não encontradas
    
    # Verifica se o arquivo tem tamanho válido (maior que 0)
    try:
        if os.path.getsize(sPath) == 0:
            return None  # Ignora arquivos vazios
    except:
        return None
    
    return sPath


def numero_por_extenso(num):
    """Converte número em texto por extenso (1-31 para dias)"""
    numeros = {
        1: 'primeiro', 2: 'dois', 3: 'três', 4: 'quatro', 5: 'cinco',
        6: 'seis', 7: 'sete', 8: 'oito', 9: 'nove', 10: 'dez',
        11: 'onze', 12: 'doze', 13: 'treze', 14: 'quatorze', 15: 'quinze',
        16: 'dezesseis', 17: 'dezessete', 18: 'dezoito', 19: 'dezenove', 20: 'vinte',
        21: 'vinte e um', 22: 'vinte e dois', 23: 'vinte e três', 24: 'vinte e quatro',
        25: 'vinte e cinco', 26: 'vinte e seis', 27: 'vinte e sete', 28: 'vinte e oito',
        29: 'vinte e nove', 30: 'trinta', 31: 'trinta e um'
    }
    return numeros.get(num, str(num))


def mes_por_extenso(mes):
    """Converte mês em texto por extenso"""
    meses = {
        1: 'janeiro', 2: 'fevereiro', 3: 'março', 4: 'abril',
        5: 'maio', 6: 'junho', 7: 'julho', 8: 'agosto',
        9: 'setembro', 10: 'outubro', 11: 'novembro', 12: 'dezembro'
    }
    return meses.get(mes, '')


def data_por_extenso(data):
    """Converte data em formato por extenso com dia em número"""
    if not data:
        return ''
    
    dia = data.day  # Mantém o dia como número
    mes = mes_por_extenso(data.month)
    ano = data.year
    
    return f"{dia} de {mes} de {ano}"


def gerar_pdf_historico(historico):
    """
    Gera PDF do histórico escolar completo (multi-ano)
    
    Args:
        historico: Objeto Historico com todas as relações carregadas
    
    Returns:
        bytes: PDF gerado em formato bytes
    """
    from models import Escola
    
    # Buscar ESCOLA PADRÃO (marcada como escola emissora de históricos)
    escola_emissora = Escola.query.filter_by(eh_escola_padrao=True).first()
    
    # Se não houver escola padrão, usar a primeira
    if not escola_emissora:
        escola_emissora = Escola.query.first()
    
    # Preparar dados para o template
    dados = {
        'historico': historico,
        'aluno': historico.aluno,
        'modalidade': historico.modalidade,
        'escola_emissora': escola_emissora,  # ESCOLA QUE EMITE O DOCUMENTO
        'anos_letivos': sorted(historico.anos_letivos, key=lambda x: x.ano),
        'data_emissao_extenso': data_por_extenso(historico.data_emissao) if historico.data_emissao else data_por_extenso(datetime.now().date()),
        'data_conclusao_extenso': data_por_extenso(historico.data_conclusao) if historico.data_conclusao else '',
        'ano_atual': datetime.now().year
    }
    
    # Calcular totais gerais (soma de todos os anos)
    total_ch = 0
    total_faltas = 0
    total_disciplinas = 0
    total_aprovadas = 0
    total_reprovadas = 0
    
    for ano_letivo in historico.anos_letivos:
        total_ch += ano_letivo.carga_horaria_total or 0
        for disc in ano_letivo.disciplinas:
            total_disciplinas += 1
            total_faltas += disc.faltas or 0
            if disc.resultado == 'A':
                total_aprovadas += 1
            elif disc.resultado == 'R':
                total_reprovadas += 1
    
    dados['totais'] = {
        'carga_horaria': total_ch,
        'faltas': total_faltas,
        'disciplinas': total_disciplinas,
        'aprovadas': total_aprovadas,
        'reprovadas': total_reprovadas
    }
    
    # Renderizar template HTML
    html_string = render_template('pdf/historico.html', **dados)
    
    # Gerar PDF com xhtml2pdf usando link_callback para processar imagens
    pdf_file = io.BytesIO()
    pisa_status = pisa.CreatePDF(
        html_string, 
        dest=pdf_file,
        link_callback=link_callback
    )
    
    if pisa_status.err:
        raise Exception(f"Erro ao gerar PDF: {pisa_status.err}")
    
    pdf_file.seek(0)
    return pdf_file.read()
