from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from models import Historico, Aluno, Escola, ModalidadeEnsino, HistoricoDisciplina, DisciplinaHistorica, HistoricoAnoLetivo, HistoricoAnoDisciplina, ResultadoFinal
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
    """Cria um novo histórico completo (multi-ano)"""
    if request.method == 'POST':
        try:
            # Criar o histórico base
            historico = Historico(
                aluno_id=request.form['aluno_id'],
                modalidade_id=request.form['modalidade_id'],
                nivel=request.form['nivel'],
                escola_origem=request.form.get('escola_origem'),
                municipio_origem=request.form.get('municipio_origem'),
                uf_origem=request.form.get('uf_origem'),
                observacoes=request.form.get('observacoes'),
                exibir_faltas_frequencia=bool(request.form.get('exibir_faltas_frequencia'))
            )
            
            db.session.add(historico)
            db.session.flush()  # Obter o ID do histórico
            
            # Processar cada ano letivo
            anos_keys = [key for key in request.form.keys() if key.startswith('anos[') and key.endswith('][ano]')]
            total_disciplinas = 0
            
            # Obter disciplinas selecionadas globalmente
            disciplinas_selecionadas = request.form.getlist('disciplinas_selecionadas[]')
            print(f"Disciplinas selecionadas: {disciplinas_selecionadas}")
            
            for ano_key in anos_keys:
                # Extrair índice do ano: anos[0][ano] -> 0
                idx = ano_key.split('[')[1].split(']')[0]
                
                # Criar ano letivo
                ano_letivo = HistoricoAnoLetivo(
                    historico_id=historico.id,
                    escola_id=int(request.form[f'anos[{idx}][escola_id]']),
                    ano=int(request.form[f'anos[{idx}][ano]']),
                    serie=request.form[f'anos[{idx}][serie]']
                )
                
                db.session.add(ano_letivo)
                db.session.flush()
                
                # Adicionar disciplinas selecionadas a este ano
                for disc_id_str in disciplinas_selecionadas:
                    disc_id = int(disc_id_str)
                    disciplina = DisciplinaHistorica.query.get(disc_id)
                    if disciplina:
                        disc_ano = HistoricoAnoDisciplina(
                            ano_letivo_id=ano_letivo.id,
                            disciplina_historica_id=disc_id,
                            carga_horaria=disciplina.carga_horaria_padrao or 0,
                            nota_final=0.0,
                            faltas=0,
                            frequencia=100.0,
                            resultado='P'  # Pendente
                        )
                        db.session.add(disc_ano)
                        total_disciplinas += 1
            
            db.session.commit()
            flash(f'Histórico criado com sucesso! {len(anos_keys)} anos letivos e {total_disciplinas} disciplinas adicionadas.', 'success')
            return redirect(url_for('historicos.lancar_notas', id=historico.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar histórico: {str(e)}', 'danger')
            import traceback
            traceback.print_exc()
    
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
    """Lançar notas e frequência das disciplinas por ano letivo"""
    historico = Historico.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Processar lançamento de notas para cada ano letivo
            for ano_letivo in historico.anos_letivos:
                # Atualizar dados do ano letivo
                ano_letivo.resultado_final_id = int(request.form.get(f'ano_{ano_letivo.id}_resultado_final_id')) if request.form.get(f'ano_{ano_letivo.id}_resultado_final_id') else None
                ano_letivo.dias_letivos = int(request.form.get(f'ano_{ano_letivo.id}_dias_letivos')) if request.form.get(f'ano_{ano_letivo.id}_dias_letivos') else None
                
                # Calcular carga horária total do ano
                ch_total = 0
                
                # Processar disciplinas do ano
                for disc_ano in ano_letivo.disciplinas:
                    nota_key = f'disc_{disc_ano.id}_nota'
                    ch_key = f'disc_{disc_ano.id}_ch'
                    faltas_key = f'disc_{disc_ano.id}_faltas'
                    resultado_key = f'disc_{disc_ano.id}_resultado'
                    
                    if nota_key in request.form:
                        disc_ano.nota_final = float(request.form[nota_key]) if request.form[nota_key] else 0.0
                        disc_ano.carga_horaria = int(request.form[ch_key]) if request.form.get(ch_key) else 0
                        disc_ano.faltas = int(request.form[faltas_key]) if request.form.get(faltas_key) else 0
                        disc_ano.resultado = request.form.get(resultado_key, 'P')
                        
                        # Calcular frequência
                        if disc_ano.carga_horaria > 0:
                            disc_ano.frequencia = ((disc_ano.carga_horaria - disc_ano.faltas) / disc_ano.carga_horaria) * 100
                        else:
                            disc_ano.frequencia = 100.0
                        
                        ch_total += disc_ano.carga_horaria
                
                # Atualizar carga horária total do ano
                ano_letivo.carga_horaria_total = ch_total
            
            # Processar conclusão de curso
            historico.conclusao_curso = bool(request.form.get('conclusao_curso'))
            historico.exibir_faltas_frequencia = bool(request.form.get('exibir_faltas_frequencia'))
            
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
            
            db.session.commit()
            flash('Notas e informações salvas com sucesso!', 'success')
            return redirect(url_for('historicos.visualizar', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao lançar notas: {str(e)}', 'danger')
            import traceback
            traceback.print_exc()
    
    # Buscar amparos legais e resultados finais para os selects
    from models.disciplina import AmparoLegal
    amparos_legais = AmparoLegal.query.order_by(AmparoLegal.ano_inicio.desc()).all()
    resultados_finais = ResultadoFinal.query.filter_by(ativo=True).all()
    
    return render_template('historicos/lancar_notas.html', 
                         historico=historico,
                         amparos_legais=amparos_legais,
                         resultados_finais=resultados_finais)

@bp.route('/visualizar/<int:id>')
def visualizar(id):
    """Visualiza um histórico completo"""
    historico = Historico.query.get_or_404(id)
    return render_template('historicos/visualizar.html', historico=historico)

@bp.route('/gerar-pdf/<int:id>')
def gerar_pdf(id):
    """Gera PDF do histórico completo"""
    try:
        historico = Historico.query.get_or_404(id)
        
        # Gerar PDF
        pdf_bytes = gerar_pdf_historico(historico)
        
        # Criar nome do arquivo com anos
        anos_str = '_'.join([str(ano.ano) for ano in sorted(historico.anos_letivos, key=lambda x: x.ano)])
        nome_arquivo = f"Historico_{historico.aluno.nome_completo.replace(' ', '_')}_{anos_str}.pdf"
        
        # Retornar PDF para download
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=nome_arquivo
        )
        
    except Exception as e:
        flash(f'Erro ao gerar PDF: {str(e)}', 'danger')
        import traceback
        traceback.print_exc()
        return redirect(url_for('historicos.visualizar', id=id))

@bp.route('/remover/<int:id>', methods=['POST'])
def remover(id):
    """Remove um histórico e todos os seus dados relacionados"""
    try:
        historico = Historico.query.get_or_404(id)
        nome_aluno = historico.aluno.nome_completo
        
        # O SQLAlchemy com cascade='all, delete-orphan' já remove automaticamente:
        # - anos_letivos
        # - disciplinas de cada ano
        # Apenas precisamos remover o histórico
        
        db.session.delete(historico)
        db.session.commit()
        
        flash(f'Histórico de {nome_aluno} removido com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao remover histórico: {str(e)}', 'danger')
        import traceback
        traceback.print_exc()
    
    return redirect(url_for('historicos.listar'))

