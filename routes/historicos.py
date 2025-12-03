from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify
from models import Historico, Aluno, Escola, ModalidadeEnsino, HistoricoDisciplina, DisciplinaHistorica, HistoricoAnoLetivo, HistoricoAnoDisciplina, ResultadoFinal
from extensions import db
from datetime import datetime
from pdf_generator.historico_pdf import gerar_pdf_historico
from database.backup import criar_backup
import io
import re

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
            
            # Obter todos os anos do formulário
            anos_keys = [key for key in request.form.keys() if key.startswith('anos[')]
            print(f"\n🔍 DEBUG: Chaves do formulário com 'anos[': {anos_keys}\n")
            print(f"📋 DEBUG: Todas as chaves do formulário:\n{list(request.form.keys())}\n")
            
            anos_dict = {}
            
            # Agrupar dados por ano
            for key in anos_keys:
                # Padrão: anos[idx][campo] ou anos[idx][disciplinas][disc_id][campo]
                if '[disciplinas]' in key:
                    continue  # Processa depois
                
                match = re.match(r'anos\[(\d+)\]\[([^\]]+)\]', key)
                if match:
                    idx = match.group(1)
                    campo = match.group(2)
                    
                    if idx not in anos_dict:
                        anos_dict[idx] = {}
                    anos_dict[idx][campo] = request.form[key]
            
            print(f"✅ DEBUG: anos_dict = {anos_dict}\n")
            
            for idx, ano_data in anos_dict.items():
                # Extrair dados do ano
                ano_value = ano_data.get('ano', '1960')
                ano = int(ano_value) if ano_value and ano_value != '' and ano_value != 'None' else 1960
                serie = ano_data.get('serie', '')
                
                print(f"📌 DEBUG: Processando ano {idx}: ano={ano}, serie={serie}")
                
                # Verificar se é escola cadastrada ou manual
                escola_id_str = ano_data.get('escola_id', '')
                escola_nome_manual = ano_data.get('escola_nome_manual', '').strip()
                escola_municipio_manual = ano_data.get('escola_municipio_manual', '').strip()
                escola_estado_manual = ano_data.get('escola_estado_manual', '').strip()
                
                # Se selecionou "outra", usar o nome manual
                if escola_id_str == 'outra' and escola_nome_manual:
                    escola_id = None
                else:
                    escola_id = int(escola_id_str) if escola_id_str and escola_id_str != 'outra' else None
                    escola_nome_manual = None
                    escola_municipio_manual = None
                    escola_estado_manual = None
                
                # Criar ano letivo
                ano_letivo = HistoricoAnoLetivo(
                    historico_id=historico.id,
                    escola_id=escola_id,
                    escola_nome_manual=escola_nome_manual,
                    escola_municipio_manual=escola_municipio_manual,
                    escola_estado_manual=escola_estado_manual,
                    ano=ano,
                    serie=serie
                )
                
                db.session.add(ano_letivo)
                db.session.flush()
                print(f"✨ DEBUG: Ano letivo criado com ID {ano_letivo.id}")
                
                # Processar disciplinas deste ano
                # Padrão: anos[idx][disciplinas][disc_id][nota]
                disciplinas_encontradas = 0
                for key in request.form.keys():
                    if f'anos[{idx}][disciplinas]' in key:
                        # Extrair disc_id - grupo 2 é o disc_id, grupo 3 é o campo
                        match = re.match(r'anos\[(\d+)\]\[disciplinas\]\[(\d+)\]\[(.+)\]', key)
                        if match:
                            disc_id_str = match.group(2)  # grupo 2 é o disc_id
                            disc_id = int(disc_id_str) if disc_id_str and disc_id_str != 'None' else None
                            if not disc_id:
                                continue
                            campo = match.group(3)  # grupo 3 é o campo (nota/faltas/resultado)
                            valor = request.form[key]
                            
                            print(f"  🎯 Encontrado: disc_id={disc_id}, campo={campo}, valor={valor}, key={key}")
                            
                            # Procura ou cria disciplina do ano
                            disc_ano = HistoricoAnoDisciplina.query.filter_by(
                                ano_letivo_id=ano_letivo.id,
                                disciplina_historica_id=disc_id
                            ).first()
                            
                            
                            if not disc_ano:
                                disciplina = DisciplinaHistorica.query.get(disc_id)
                                if disciplina:
                                    disc_ano = HistoricoAnoDisciplina(
                                        ano_letivo_id=ano_letivo.id,
                                        disciplina_historica_id=disc_id,
                                        carga_horaria=disciplina.carga_horaria_padrao or 0,
                                        nota_final=0.0,
                                        faltas=0,
                                        frequencia=100.0,
                                        resultado='P'
                                    )
                                    db.session.add(disc_ano)
                                    db.session.flush()
                            
                            # Atualizar campo da disciplina
                            if disc_ano:
                                if campo == 'nota':
                                    try:
                                        disc_ano.nota_final = float(valor) if valor else 0.0
                                        print(f"    ✅ Nota salva: {disc_ano.nota_final}")
                                    except:
                                        disc_ano.nota_final = 0.0
                                elif campo == 'faltas':
                                    disc_ano.faltas = int(valor) if valor and valor != '' and valor != 'None' else 0
                                elif campo == 'resultado':
                                    disc_ano.resultado = valor or 'P'
                            
                            total_disciplinas += 1
                            disciplinas_encontradas += 1
                
                print(f"  📊 Total de disciplinas encontradas para ano {idx}: {disciplinas_encontradas}\n")
            
            print(f"\n🎉 DEBUG: Totalizando {len(anos_dict)} anos e {total_disciplinas} disciplinas\n")
            
            db.session.commit()
            flash(f'Histórico criado com sucesso! {len(anos_dict)} anos letivos e {total_disciplinas} disciplinas adicionadas.', 'success')
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

@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    """Edita um histórico existente"""
    from database.backup import criar_backup
    
    historico = Historico.query.options(
        db.joinedload(Historico.anos_letivos).joinedload(HistoricoAnoLetivo.disciplinas)
    ).get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Criar backup antes de editar
            backup_path = criar_backup()
            print(f"📦 Backup criado: {backup_path}")
            
            # Atualizar dados básicos do histórico
            historico.aluno_id = request.form['aluno_id']
            historico.modalidade_id = request.form['modalidade_id']
            historico.nivel = request.form['nivel']
            historico.escola_origem = request.form.get('escola_origem')
            historico.municipio_origem = request.form.get('municipio_origem')
            historico.uf_origem = request.form.get('uf_origem')
            historico.observacoes = request.form.get('observacoes')
            historico.exibir_faltas_frequencia = bool(request.form.get('exibir_faltas_frequencia'))
            
            # Remover anos letivos antigos
            for ano_antigo in historico.anos_letivos:
                db.session.delete(ano_antigo)
            db.session.flush()
            
            # Processar novos anos letivos (mesmo código do /novo)
            anos_keys = [key for key in request.form.keys() if key.startswith('anos[')]
            print(f"\n🔍 DEBUG EDITAR: Chaves do formulário com 'anos[': {anos_keys}\n")
            
            anos_dict = {}
            total_disciplinas = 0
            
            # Agrupar dados por ano
            for key in anos_keys:
                if '[disciplinas]' in key:
                    continue
                
                match = re.match(r'anos\[(\d+)\]\[([^\]]+)\]', key)
                if match:
                    idx = match.group(1)
                    campo = match.group(2)
                    
                    if idx not in anos_dict:
                        anos_dict[idx] = {}
                    anos_dict[idx][campo] = request.form[key]
            
            print(f"✅ DEBUG EDITAR: anos_dict = {anos_dict}\n")
            
            for idx, ano_data in anos_dict.items():
                ano_value = ano_data.get('ano', '1960')
                ano = int(ano_value) if ano_value and ano_value != '' and ano_value != 'None' else 1960
                serie = ano_data.get('serie', '')
                
                escola_id_str = ano_data.get('escola_id', '')
                escola_nome_manual = ano_data.get('escola_nome_manual', '').strip()
                escola_municipio_manual = ano_data.get('escola_municipio_manual', '').strip()
                escola_estado_manual = ano_data.get('escola_estado_manual', '').strip()
                
                if escola_id_str == 'outra' and escola_nome_manual:
                    escola_id = None
                else:
                    escola_id = int(escola_id_str) if escola_id_str and escola_id_str != 'outra' and escola_id_str != 'None' else None
                    escola_nome_manual = None
                    escola_municipio_manual = None
                    escola_estado_manual = None
                
                ano_letivo = HistoricoAnoLetivo(
                    historico_id=historico.id,
                    escola_id=escola_id,
                    escola_nome_manual=escola_nome_manual,
                    escola_municipio_manual=escola_municipio_manual,
                    escola_estado_manual=escola_estado_manual,
                    ano=ano,
                    serie=serie
                )
                
                db.session.add(ano_letivo)
                db.session.flush()
                
                # Processar disciplinas do ano
                disciplinas_encontradas = 0
                disc_keys = [k for k in request.form.keys() if k.startswith(f'anos[{idx}][disciplinas]')]
                
                for disc_key in disc_keys:
                    match = re.match(r'anos\[' + idx + r'\]\[disciplinas\]\[(\d+)\]\[nota\]', disc_key)
                    if match:
                        disc_id_str = match.group(1)
                        disc_id = int(disc_id_str) if disc_id_str and disc_id_str != 'None' else None
                        if not disc_id:
                            continue
                        nota_value = request.form[disc_key].strip()
                        
                        if nota_value:
                            ano_disciplina = HistoricoAnoDisciplina(
                                ano_letivo_id=ano_letivo.id,
                                disciplina_id=disc_id,
                                nota=nota_value
                            )
                            db.session.add(ano_disciplina)
                            total_disciplinas += 1
                            disciplinas_encontradas += 1
                
                print(f"  📊 Total de disciplinas para ano {idx}: {disciplinas_encontradas}\n")
            
            print(f"\n🎉 DEBUG EDITAR: Totalizando {len(anos_dict)} anos e {total_disciplinas} disciplinas\n")
            
            db.session.commit()
            flash(f'Histórico atualizado com sucesso! {len(anos_dict)} anos letivos e {total_disciplinas} disciplinas.', 'success')
            return redirect(url_for('historicos.lancar_notas', id=historico.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao editar histórico: {str(e)}', 'danger')
            import traceback
            traceback.print_exc()
    
    # GET - Carregar dados para edição
    alunos = Aluno.query.filter_by(ativo=True).all()
    escolas = Escola.query.filter_by(ativa=True).all()
    modalidades = ModalidadeEnsino.query.filter_by(ativa=True).all()
    disciplinas = DisciplinaHistorica.query.filter_by(ativa=True).order_by(DisciplinaHistorica.nome).all()
    
    return render_template('historicos/editar.html', 
                         historico=historico,
                         alunos=alunos, 
                         escolas=escolas, 
                         modalidades=modalidades,
                         disciplinas=disciplinas)

@bp.route('/lancar-notas/<int:id>', methods=['GET', 'POST'])
def lancar_notas(id):
    """Lançar notas e frequência das disciplinas por ano letivo"""
    historico = Historico.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            print("DEBUG: Dados do formulário recebidos:")
            for key, value in request.form.items():
                print(f"  {key} = {value}")
            
            # Processar lançamento de notas para cada ano letivo
            for ano_letivo in historico.anos_letivos:
                # Atualizar dados do ano letivo
                resultado_final_value = request.form.get(f'ano_{ano_letivo.id}_resultado_final_id')
                ano_letivo.resultado_final_id = int(resultado_final_value) if resultado_final_value and resultado_final_value != '' else None
                
                # Calcular carga horária total do ano
                ch_total = 0
                
                # Processar disciplinas do ano
                for disc_ano in ano_letivo.disciplinas:
                    nota_key = f'disc_{disc_ano.id}_nota'
                    ch_key = f'disc_{disc_ano.id}_ch'
                    faltas_key = f'disc_{disc_ano.id}_faltas'
                    resultado_key = f'disc_{disc_ano.id}_resultado'
                    
                    if nota_key in request.form:
                        nota_value = request.form.get(nota_key)
                        ch_value = request.form.get(ch_key)
                        faltas_value = request.form.get(faltas_key)
                        
                        disc_ano.nota_final = float(nota_value) if nota_value and nota_value != '' else 0.0
                        disc_ano.carga_horaria = int(ch_value) if ch_value and ch_value != '' else 0
                        disc_ano.faltas = int(faltas_value) if faltas_value and faltas_value != '' else 0
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
                # Converter ano_conclusao para data (usando 1º de janeiro do ano)
                ano_conclusao = request.form.get('ano_conclusao')
                if ano_conclusao and ano_conclusao != '':
                    historico.data_conclusao = datetime(int(ano_conclusao), 1, 1).date()
                else:
                    historico.data_conclusao = None
                
                amparo_value = request.form.get('amparo_conclusao_id')
                historico.amparo_conclusao_id = int(amparo_value) if amparo_value and amparo_value != '' else None
            
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
        # Carregar histórico com TODAS as relações necessárias (eager loading)
        historico = Historico.query.options(
            db.joinedload(Historico.anos_letivos)
              .joinedload(HistoricoAnoLetivo.disciplinas)
              .joinedload(HistoricoAnoDisciplina.disciplina_historica)
        ).get_or_404(id)
        
        print(f"\n📄 DEBUG PDF: Gerando PDF para histórico ID {id}")
        print(f"📊 Anos letivos: {len(historico.anos_letivos)}")
        for ano in historico.anos_letivos:
            print(f"  📅 Ano {ano.ano}: {len(ano.disciplinas)} disciplinas")
            for disc in ano.disciplinas:
                print(f"    - {disc.disciplina_historica.nome}: nota={disc.nota_final}")
        
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

@bp.route('/auto-save', methods=['POST'])
def auto_save():
    """Salva automaticamente o histórico em progresso"""
    try:
        data = request.get_json()
        historico_id = data.get('historico_id')
        
        # Se já existe ID, atualizar
        if historico_id:
            historico = Historico.query.get(historico_id)
            if not historico:
                return jsonify({'success': False, 'error': 'Histórico não encontrado'}), 404
        else:
            # Criar novo histórico temporário
            historico = Historico(
                aluno_id=data['aluno_id'],
                modalidade_id=data['modalidade_id'],
                nivel=data['nivel'],
                escola_origem=data.get('escola_origem'),
                municipio_origem=data.get('municipio_origem'),
                uf_origem=data.get('uf_origem'),
                observacoes=data.get('observacoes'),
                exibir_faltas_frequencia=data.get('exibir_faltas_frequencia', False)
            )
            db.session.add(historico)
            db.session.flush()
        
        # Atualizar campos básicos
        historico.aluno_id = data['aluno_id']
        historico.modalidade_id = data['modalidade_id']
        historico.nivel = data['nivel']
        historico.escola_origem = data.get('escola_origem')
        historico.municipio_origem = data.get('municipio_origem')
        historico.uf_origem = data.get('uf_origem')
        historico.observacoes = data.get('observacoes')
        historico.exibir_faltas_frequencia = data.get('exibir_faltas_frequencia', False)
        
        # Remover anos antigos
        for ano_antigo in historico.anos_letivos:
            db.session.delete(ano_antigo)
        db.session.flush()
        
        # Adicionar anos novos
        anos_data = data.get('anos', [])
        for ano_info in anos_data:
            ano_letivo = HistoricoAnoLetivo(
                historico_id=historico.id,
                escola_id=ano_info.get('escola_id') if ano_info.get('escola_id') != 'outra' else None,
                escola_nome_manual=ano_info.get('escola_nome_manual'),
                escola_municipio_manual=ano_info.get('escola_municipio_manual'),
                escola_estado_manual=ano_info.get('escola_estado_manual'),
                ano=ano_info['ano'],
                serie=ano_info['serie']
            )
            db.session.add(ano_letivo)
            db.session.flush()
            
            # Adicionar disciplinas do ano
            for disc_info in ano_info.get('disciplinas', []):
                ano_disciplina = HistoricoAnoDisciplina(
                    ano_letivo_id=ano_letivo.id,
                    disciplina_id=disc_info['disciplina_id'],
                    nota=disc_info.get('nota')
                )
                db.session.add(ano_disciplina)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'historico_id': historico.id,
            'message': 'Dados salvos automaticamente'
        })
        
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

