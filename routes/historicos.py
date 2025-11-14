from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models import Historico, Aluno, Escola, ModalidadeEnsino, HistoricoDisciplina, DisciplinaHistorica
from extensions import db
from datetime import datetime
from pdf_generator.historico_pdf import gerar_pdf_historico
import io

bp = Blueprint('historicos', __name__, url_prefix='/historicos')

@bp.route('/')
def listar():
    """Lista todos os históricos"""
    historicos = Historico.query.all()
    return render_template('historicos/listar.html', historicos=historicos)

@bp.route('/novo', methods=['GET', 'POST'])
def novo():
    """Cria um novo histórico"""
    if request.method == 'POST':
        try:
            # Verificar se há disciplinas selecionadas
            disciplinas_selecionadas = request.form.getlist('disciplinas_selecionadas[]')
            
            if not disciplinas_selecionadas:
                flash('Selecione pelo menos uma disciplina para o histórico!', 'warning')
                alunos = Aluno.query.filter_by(ativo=True).all()
                escolas = Escola.query.filter_by(ativa=True).all()
                modalidades = ModalidadeEnsino.query.filter_by(ativa=True).all()
                return render_template('historicos/novo.html', 
                                     alunos=alunos, 
                                     escolas=escolas, 
                                     modalidades=modalidades)
            
            # Criar o histórico
            historico = Historico(
                aluno_id=request.form['aluno_id'],
                escola_id=request.form['escola_id'],
                ano=int(request.form['ano']),
                serie=request.form['serie'],
                modalidade_id=request.form['modalidade_id'],
                nivel=request.form['nivel'],
                data_inicio=datetime.strptime(request.form['data_inicio'], '%Y-%m-%d').date() if request.form.get('data_inicio') else None,
                data_termino=datetime.strptime(request.form['data_termino'], '%Y-%m-%d').date() if request.form.get('data_termino') else None,
                escola_origem=request.form.get('escola_origem'),
                municipio_origem=request.form.get('municipio_origem'),
                uf_origem=request.form.get('uf_origem'),
                observacoes=request.form.get('observacoes')
            )
            
            db.session.add(historico)
            db.session.flush()  # Obter o ID do histórico antes de adicionar disciplinas
            
            # Adicionar disciplinas selecionadas ao histórico
            for disciplina_id in disciplinas_selecionadas:
                disciplina = DisciplinaHistorica.query.get(int(disciplina_id))
                if disciplina:
                    historico_disciplina = HistoricoDisciplina(
                        historico_id=historico.id,
                        disciplina_historica_id=disciplina.id,
                        carga_horaria=disciplina.carga_horaria_padrao or 0,
                        nota_final=0.0,  # Será preenchida no lançamento de notas
                        faltas=0,
                        frequencia=100.0,
                        resultado='P'  # Pendente
                    )
                    db.session.add(historico_disciplina)
            
            db.session.commit()
            flash(f'Histórico criado com sucesso! {len(disciplinas_selecionadas)} disciplinas adicionadas.', 'success')
            return redirect(url_for('historicos.lancar_notas', id=historico.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar histórico: {str(e)}', 'danger')
    
    # Dados para o formulário
    alunos = Aluno.query.filter_by(ativo=True).all()
    escolas = Escola.query.filter_by(ativa=True).all()
    modalidades = ModalidadeEnsino.query.filter_by(ativa=True).all()
    
    return render_template('historicos/novo.html', 
                         alunos=alunos, 
                         escolas=escolas, 
                         modalidades=modalidades)

@bp.route('/lancar-notas/<int:id>', methods=['GET', 'POST'])
def lancar_notas(id):
    """Lançar notas e frequência das disciplinas"""
    historico = Historico.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Processar lançamento de notas para cada disciplina
            disciplinas_historico = HistoricoDisciplina.query.filter_by(historico_id=id).all()
            
            for disc_hist in disciplinas_historico:
                # Capturar dados do formulário
                nota_key = f'nota_{disc_hist.id}'
                ch_key = f'ch_{disc_hist.id}'
                faltas_key = f'faltas_{disc_hist.id}'
                resultado_key = f'resultado_{disc_hist.id}'
                
                if nota_key in request.form:
                    disc_hist.nota_final = float(request.form[nota_key]) if request.form[nota_key] else 0.0
                    disc_hist.carga_horaria = int(request.form[ch_key]) if request.form.get(ch_key) else 0
                    disc_hist.faltas = int(request.form[faltas_key]) if request.form.get(faltas_key) else 0
                    disc_hist.resultado = request.form.get(resultado_key, 'P')
                    
                    # Calcular frequência
                    if disc_hist.carga_horaria > 0:
                        disc_hist.frequencia = ((disc_hist.carga_horaria - disc_hist.faltas) / disc_hist.carga_horaria) * 100
                    else:
                        disc_hist.frequencia = 100.0
            
            # Processar conclusão de curso
            historico.conclusao_curso = bool(request.form.get('conclusao_curso'))
            
            if historico.conclusao_curso:
                historico.data_conclusao = datetime.strptime(request.form['data_conclusao'], '%Y-%m-%d').date() if request.form.get('data_conclusao') else None
                historico.amparo_conclusao_id = int(request.form['amparo_conclusao_id']) if request.form.get('amparo_conclusao_id') else None
                historico.numero_certificado = request.form.get('numero_certificado')
                historico.livro_registro = request.form.get('livro_registro')
                historico.folha_registro = request.form.get('folha_registro')
            
            # Processar assinaturas e dados adicionais
            historico.nome_diretor = request.form.get('nome_diretor')
            historico.nome_secretario = request.form.get('nome_secretario')
            historico.data_emissao = datetime.strptime(request.form['data_emissao'], '%Y-%m-%d').date() if request.form.get('data_emissao') else None
            historico.dias_letivos = int(request.form['dias_letivos']) if request.form.get('dias_letivos') else None
            
            db.session.commit()
            flash('Notas e informações salvas com sucesso!', 'success')
            return redirect(url_for('historicos.visualizar', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao lançar notas: {str(e)}', 'danger')
    
    # Buscar disciplinas do histórico (já selecionadas)
    disciplinas_historico = HistoricoDisciplina.query.filter_by(historico_id=id).all()
    
    # Buscar amparos legais para o select de conclusão
    from models.disciplina import AmparoLegal
    amparos_legais = AmparoLegal.query.order_by(AmparoLegal.ano_inicio.desc()).all()
    
    return render_template('historicos/lancar_notas.html', 
                         historico=historico, 
                         disciplinas=disciplinas_historico,
                         amparos_legais=amparos_legais)

@bp.route('/visualizar/<int:id>')
def visualizar(id):
    """Visualiza um histórico completo"""
    historico = Historico.query.get_or_404(id)
    return render_template('historicos/visualizar.html', historico=historico)

@bp.route('/gerar-pdf/<int:id>')
def gerar_pdf(id):
    """Gera PDF do histórico"""
    try:
        historico = Historico.query.get_or_404(id)
        
        # Gerar PDF
        pdf_bytes = gerar_pdf_historico(historico)
        
        # Criar nome do arquivo
        nome_arquivo = f"Historico_{historico.aluno.nome_completo.replace(' ', '_')}_{historico.ano}_{historico.serie.replace(' ', '_')}.pdf"
        
        # Retornar PDF para download
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=nome_arquivo
        )
        
    except Exception as e:
        flash(f'Erro ao gerar PDF: {str(e)}', 'danger')
        return redirect(url_for('historicos.visualizar', id=id))
