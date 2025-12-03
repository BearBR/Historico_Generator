from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import DisciplinaHistorica, ModalidadeEnsino
from extensions import db

bp = Blueprint('disciplinas', __name__, url_prefix='/disciplinas')

@bp.route('/')
def listar():
    """Lista todas as disciplinas"""
    disciplinas = DisciplinaHistorica.query.filter_by(ativa=True).order_by(DisciplinaHistorica.nome).all()
    return render_template('disciplinas/listar.html', disciplinas=disciplinas)

@bp.route('/por-ano/<int:ano>')
def por_ano(ano):
    """Lista disciplinas disponíveis em um ano específico"""
    disciplinas = DisciplinaHistorica.query.filter(
        DisciplinaHistorica.ano_inicio <= ano,
        (DisciplinaHistorica.ano_fim >= ano) | (DisciplinaHistorica.ano_fim == None),
        DisciplinaHistorica.ativa == True
    ).order_by(DisciplinaHistorica.nome).all()
    
    return render_template('disciplinas/por_ano.html', disciplinas=disciplinas, ano=ano)

@bp.route('/api/buscar')
def buscar_disciplinas():
    """API: Busca disciplinas por nome ou código"""
    termo = request.args.get('termo', '').strip()
    
    if len(termo) < 2:
        return jsonify({'disciplinas': []})
    
    # Buscar disciplinas que contenham o termo
    disciplinas = DisciplinaHistorica.query.filter(
        DisciplinaHistorica.ativa == True,
        db.or_(
            DisciplinaHistorica.nome.ilike(f'%{termo}%'),
            DisciplinaHistorica.codigo.ilike(f'%{termo}%')
        )
    ).order_by(DisciplinaHistorica.nome).limit(20).all()
    
    return jsonify({
        'disciplinas': [{
            'id': d.id,
            'nome': d.nome,
            'codigo': d.codigo,
            'carga_horaria_padrao': d.carga_horaria_padrao
        } for d in disciplinas]
    })

@bp.route('/api/carregar-grade')
def carregar_grade():
    """API: Carrega automaticamente grade curricular por ano, modalidade e nível"""
    ano = request.args.get('ano', type=int, default=1980)
    modalidade = request.args.get('modalidade', 'Regular')
    nivel = request.args.get('nivel', 'Fundamental')
    
    # Buscar TODAS as disciplinas ativas
    disciplinas = DisciplinaHistorica.query.filter(
        DisciplinaHistorica.ano_inicio <= ano,
        DisciplinaHistorica.ativa == True
    ).filter(
        db.or_(DisciplinaHistorica.ano_fim.is_(None), DisciplinaHistorica.ano_fim >= ano)
    ).order_by(DisciplinaHistorica.nome).all()
    
    # Filtrar por palavras-chave do nível e modalidade
    disciplinas_filtradas = []
    for d in disciplinas:
        # Filtro por série/nível
        serie_lower = (d.serie or '').lower()
        
        # Lógica de filtro específica por modalidade e período
        incluir = False
        
        if modalidade == 'EJA':
            # EJA tem lógica específica
            if nivel == 'Fundamental' and ('eja fund' in serie_lower or 'etapa' in serie_lower):
                incluir = True
            elif nivel == 'Médio' and ('eja médio' in serie_lower or 'totalidade' in serie_lower):
                incluir = True
            elif 'eja' in serie_lower and 'todas' in serie_lower:
                incluir = True
                
        elif modalidade == 'Supletivo':
            # Supletivo 1º e 2º Grau
            if nivel == 'Fundamental' and ('1º grau' in serie_lower or 'supletivo' in serie_lower):
                incluir = True
            elif nivel == 'Médio' and ('2º grau' in serie_lower or 'supletivo' in serie_lower):
                incluir = True
                
        elif modalidade == 'Regular':
            # Regular - filtro por período histórico
            if ano <= 1971:
                # Período LDB 4024/61
                if nivel == 'Fundamental':
                    incluir = 'primário' in serie_lower or 'ginásio' in serie_lower or 'todas' in serie_lower
                elif nivel == 'Médio':
                    incluir = 'colegial' in serie_lower or 'médio' in serie_lower
                    
            elif ano <= 1996:
                # Período LDB 5692/71 - 1º e 2º Grau
                if nivel == 'Fundamental':
                    incluir = '1º grau' in serie_lower or 'fundamental' in serie_lower or 'todas' in serie_lower
                elif nivel == 'Médio':
                    incluir = '2º grau' in serie_lower or 'médio' in serie_lower or 'técnico' in serie_lower
                    
            else:
                # Período LDB 9394/96
                if nivel == 'Fundamental':
                    incluir = 'fundamental' in serie_lower or 'todas' in serie_lower
                elif nivel == 'Médio':
                    incluir = 'médio' in serie_lower or 'todas' in serie_lower
        
        # Se não tem filtro de série, incluir disciplinas universais
        if not d.serie or 'todas' in serie_lower.lower():
            incluir = True
            
        if incluir:
            disciplinas_filtradas.append(d)
    
    # Retornar disciplinas em formato JSON
    return jsonify({
        'disciplinas': [
            {
                'id': d.id,
                'nome': d.nome,
                'codigo': d.codigo,
                'carga_horaria_padrao': d.carga_horaria_padrao,
                'serie': d.serie
            }
            for d in disciplinas_filtradas
        ],
        'total': len(disciplinas_filtradas),
        'parametros': {
            'ano': ano,
            'modalidade': modalidade,
            'nivel': nivel
        }
    })

@bp.route('/cadastrar_rapido', methods=['POST'])
def cadastrar_rapido():
    """Cadastra uma disciplina rapidamente via AJAX"""
    try:
        data = request.get_json()
        nome = data.get('nome', '').strip()
        nome_upper = nome.upper()
        
        if not nome:
            return jsonify({'success': False, 'message': 'Nome da disciplina é obrigatório'}), 400
        
        # Verificar se já existe
        disciplina_existente = DisciplinaHistorica.query.filter(
            db.func.upper(DisciplinaHistorica.nome) == nome_upper,
            DisciplinaHistorica.ativa == True
        ).first()
        if disciplina_existente:
            return jsonify({
                'success': True, 
                'message': 'Disciplina já existe no sistema',
                'disciplina_id': disciplina_existente.id
            })
        
        # Criar nova disciplina com dados mínimos
        disciplina = DisciplinaHistorica(
            nome=nome_upper,
            ano_inicio=data.get('ano_inicio', 1960),
            ano_fim=data.get('ano_fim', 2003),
            carga_horaria_padrao=data.get('carga_horaria_padrao', 60)
        )
        
        db.session.add(disciplina)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Disciplina cadastrada com sucesso',
            'disciplina_id': disciplina.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/api/todas')
def todas_disciplinas():
    """API: Retorna todas as disciplinas ativas"""
    disciplinas = DisciplinaHistorica.query.filter_by(ativa=True).order_by(DisciplinaHistorica.nome).all()
    return jsonify({
        'disciplinas': [
            {
                'id': d.id,
                'nome': d.nome,
                'codigo': d.codigo,
                'carga_horaria_padrao': d.carga_horaria_padrao
            } for d in disciplinas
        ]
    })
