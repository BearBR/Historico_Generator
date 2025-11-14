import sqlite3
import os

def init_db():
    """Inicializa o banco de dados"""
    db_path = 'database/historicos_escolares.db'
    
    # Criar diretório se não existir
    os.makedirs('database', exist_ok=True)
    
    # Verificar se banco já existe
    if os.path.exists(db_path):
        resposta = input("Banco de dados já existe! Deseja recriar? (s/n): ")
        if resposta.lower() != 's':
            print("Operação cancelada.")
            return
        os.remove(db_path)
    
    print("Criando banco de dados...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Ler e executar schema.sql
    with open('database/schema.sql', 'r', encoding='utf-8') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    # Popular dados iniciais
    print("Populando modalidades de ensino...")
    popular_modalidades(cursor)
    
    print("Populando amparos legais...")
    popular_amparos_legais(cursor)
    
    print("Populando resultados finais...")
    popular_resultados_finais(cursor)
    
    print("Populando disciplinas históricas...")
    popular_disciplinas_historicas(cursor)
    
    print("Adicionando escola exemplo...")
    popular_escola_exemplo(cursor)
    
    conn.commit()
    conn.close()
    
    print("\n✅ Banco de dados criado com sucesso!")
    print(f"📁 Localização: {os.path.abspath(db_path)}")

def popular_modalidades(cursor):
    """Popula modalidades de ensino"""
    modalidades = [
        ('Regular', 'Ensino Regular', 1960, None),
        ('Supletivo', 'Ensino Supletivo', 1971, 1996),
        ('EJA', 'Educação de Jovens e Adultos', 1996, None),
    ]
    
    cursor.executemany('''
        INSERT INTO modalidades_ensino (nome, descricao, ano_inicio, ano_fim)
        VALUES (?, ?, ?, ?)
    ''', modalidades)

def popular_amparos_legais(cursor):
    """Popula amparos legais históricos"""
    amparos = [
        ('Lei', 'LDB 4024/61', '1961-12-20', 'Lei de Diretrizes e Bases da Educação Nacional', 1961, 1971),
        ('Lei', 'LDB 5692/71', '1971-08-11', 'Reforma do ensino de 1º e 2º graus', 1971, 1996),
        ('Lei', 'LDB 9394/96', '1996-12-20', 'Lei de Diretrizes e Bases da Educação Nacional (atual)', 1996, None),
        ('Resolução', 'CNE/CEB 03/98', '1998-06-26', 'Institui as Diretrizes Curriculares Nacionais para o Ensino Médio', 1998, None),
        ('Parecer', 'CNE/CEB 15/98', '1998-06-01', 'Diretrizes Curriculares Nacionais para o Ensino Médio', 1998, None),
    ]
    
    cursor.executemany('''
        INSERT INTO amparos_legais (tipo, numero, data, descricao, ano_inicio, ano_fim)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', amparos)

def popular_resultados_finais(cursor):
    """Popula códigos de resultado final"""
    resultados = [
        ('AP', 'Aprovado', 'aprovado', 1960, None),
        ('RP', 'Reprovado', 'reprovado', 1960, None),
        ('EX', 'Exame', 'exame', 1960, 2000),
        ('DI', 'Dispensado', 'dispensado', 1960, None),
        ('TR', 'Transferido', 'transferido', 1960, None),
        ('CA', 'Cancelado', 'cancelado', 1960, None),
        ('AB', 'Abandono', 'abandono', 1960, None),
        ('CU', 'Cursando', 'cursando', 1960, None),
    ]
    
    cursor.executemany('''
        INSERT INTO resultados_finais (codigo, descricao, tipo, ano_inicio, ano_fim)
        VALUES (?, ?, ?, ?, ?)
    ''', resultados)

def popular_disciplinas_historicas(cursor):
    """Popula disciplinas históricas do RS de 1960 até 2003"""
    
    # ========================================
    # PERÍODO LDB 4024/61 (1960-1971)
    # Ensino Primário e Ginasial
    # ========================================
    disciplinas_1960_1971 = [
        # Núcleo Comum - Primário (1ª a 4ª série)
        ('Língua Portuguesa', 'PORT', 1960, 2003, 200, 'Todas'),
        ('Matemática', 'MAT', 1960, 2003, 160, 'Todas'),
        ('História do Brasil', 'HIST', 1960, 1971, 60, '3ª e 4ª'),
        ('Geografia do Brasil', 'GEO', 1960, 1971, 60, '3ª e 4ª'),
        ('Ciências Naturais', 'CIEN', 1960, 1971, 80, 'Todas'),
        ('Desenho', 'DES', 1960, 1971, 40, 'Todas'),
        ('Trabalhos Manuais', 'TRAB', 1960, 1971, 60, 'Todas'),
        ('Canto Orfeônico', 'CANT', 1960, 1971, 40, 'Todas'),
        ('Educação Física', 'EDFIS', 1960, 2003, 80, 'Todas'),
        ('Educação Moral e Cívica', 'EMC', 1969, 1993, 40, 'Todas'),
        
        # Ginásio (5ª a 8ª série) - 1960-1971
        ('Francês', 'FRAN', 1960, 1971, 80, '5ª a 8ª'),
        ('Inglês', 'ING', 1960, 2003, 80, 'Todas'),
        ('Latim', 'LAT', 1960, 1971, 60, '7ª e 8ª'),
        
        # Colegial (Ensino Médio) - 1960-1971
        ('Física', 'FIS', 1960, 2003, 120, 'Médio'),
        ('Química', 'QUIM', 1960, 2003, 120, 'Médio'),
        ('Biologia', 'BIO', 1960, 2003, 120, 'Médio'),
        ('Filosofia', 'FIL', 1960, 1971, 80, 'Médio'),
    ]
    
    # ========================================
    # PERÍODO LDB 5692/71 (1971-1996)
    # 1º Grau (8 anos) e 2º Grau (3 anos)
    # ========================================
    disciplinas_1971_1996 = [
        # Núcleo Comum - 1º Grau (1ª a 8ª série)
        ('Comunicação e Expressão', 'COMEXP', 1971, 1996, 200, '1º Grau'),
        ('Estudos Sociais', 'ESTSOC', 1971, 1996, 120, '1º Grau'),
        ('Ciências', 'CIEN', 1971, 1996, 120, '1º Grau'),
        ('Matemática', 'MAT', 1971, 2003, 160, 'Todas'),
        
        # OSPB - Obrigatória por lei
        ('OSPB', 'OSPB', 1971, 1993, 60, 'Todas'),
        ('Educação Moral e Cívica', 'EMC', 1971, 1993, 40, 'Todas'),
        
        # Educação Artística
        ('Educação Artística', 'EARTE', 1971, 1996, 80, 'Todas'),
        
        # Programa de Saúde
        ('Programa de Saúde', 'PSAU', 1971, 1996, 40, 'Todas'),
        
        # Ensino Religioso (Facultativo)
        ('Ensino Religioso', 'ENSREL', 1971, 2003, 40, 'Facultativo'),
        
        # Língua Estrangeira Moderna
        ('Língua Estrangeira Moderna', 'LEM', 1971, 1996, 80, '5ª a 8ª'),
        
        # 2º Grau - Núcleo Comum (1971-1996)
        ('Língua Portuguesa e Literatura', 'PORT', 1971, 2003, 160, 'Médio'),
        ('História', 'HIST', 1971, 2003, 80, 'Médio'),
        ('Geografia', 'GEO', 1971, 2003, 80, 'Médio'),
        
        # Habilitações Profissionais - 2º Grau (RS)
        ('Técnicas Comerciais', 'TECCOM', 1971, 1996, 160, 'Médio Técnico'),
        ('Contabilidade', 'CONT', 1971, 1996, 160, 'Médio Técnico'),
        ('Administração', 'ADM', 1971, 1996, 120, 'Médio Técnico'),
        ('Secretariado', 'SEC', 1971, 1996, 120, 'Médio Técnico'),
        ('Datilografia', 'DATIL', 1971, 1996, 80, 'Médio Técnico'),
        ('Mecanografia', 'MECA', 1971, 1990, 80, 'Médio Técnico'),
        
        # Técnicas Agrícolas (comum no RS)
        ('Técnicas Agrícolas', 'TECAGR', 1971, 1996, 200, 'Médio Técnico'),
        ('Zootecnia', 'ZOO', 1971, 1996, 120, 'Médio Técnico'),
        ('Agricultura Geral', 'AGRI', 1971, 1996, 160, 'Médio Técnico'),
        
        # Técnicas Industriais
        ('Técnicas Industriais', 'TECIND', 1971, 1996, 160, 'Médio Técnico'),
        ('Mecânica', 'MEC', 1971, 1996, 200, 'Médio Técnico'),
        ('Eletrotécnica', 'ELET', 1971, 1996, 200, 'Médio Técnico'),
        ('Eletrônica', 'ELETRON', 1971, 1996, 200, 'Médio Técnico'),
        
        # Educação para o Lar (comum nos anos 70-80)
        ('Educação para o Lar', 'EDLAR', 1971, 1990, 80, 'Feminino'),
        ('Economia Doméstica', 'ECODOM', 1971, 1990, 60, 'Feminino'),
        ('Artes Aplicadas', 'ARTAPL', 1971, 1990, 80, 'Feminino'),
    ]
    
    # ========================================
    # PERÍODO LDB 9394/96 (1996-2003)
    # Ensino Fundamental (9 anos) e Ensino Médio
    # ========================================
    disciplinas_1996_2003 = [
        # Ensino Fundamental - Anos Iniciais (1ª a 4ª série / 1º ao 5º ano)
        ('Língua Portuguesa', 'PORT', 1996, 2003, 200, 'Fundamental'),
        ('Matemática', 'MAT', 1996, 2003, 160, 'Fundamental'),
        ('Ciências', 'CIEN', 1996, 2003, 80, 'Fundamental'),
        ('História', 'HIST', 1996, 2003, 80, 'Fundamental'),
        ('Geografia', 'GEO', 1996, 2003, 80, 'Fundamental'),
        ('Arte', 'ARTE', 1996, 2003, 80, 'Fundamental'),
        ('Educação Física', 'EDFIS', 1996, 2003, 80, 'Fundamental'),
        
        # Ensino Fundamental - Anos Finais (5ª a 8ª série / 6º ao 9º ano)
        ('Língua Estrangeira Moderna - Inglês', 'ING', 1996, 2003, 80, '5ª a 8ª'),
        ('Língua Estrangeira Moderna - Espanhol', 'ESP', 1996, 2003, 80, 'Optativa'),
        
        # Ensino Médio (1996-2003) - LDB 9394/96
        ('Língua Portuguesa', 'PORT', 1996, 2003, 160, 'Médio'),
        ('Matemática', 'MAT', 1996, 2003, 160, 'Médio'),
        ('Física', 'FIS', 1996, 2003, 120, 'Médio'),
        ('Química', 'QUIM', 1996, 2003, 120, 'Médio'),
        ('Biologia', 'BIO', 1996, 2003, 120, 'Médio'),
        ('História', 'HIST', 1996, 2003, 80, 'Médio'),
        ('Geografia', 'GEO', 1996, 2003, 80, 'Médio'),
        ('Filosofia', 'FIL', 1996, 2003, 60, 'Médio'),
        ('Sociologia', 'SOC', 1996, 2003, 60, 'Médio'),
        ('Arte', 'ARTE', 1996, 2003, 80, 'Médio'),
        ('Educação Física', 'EDFIS', 1996, 2003, 80, 'Médio'),
        ('Língua Estrangeira - Inglês', 'ING', 1996, 2003, 80, 'Médio'),
        
        # Informática (introduzida nos anos 2000)
        ('Informática', 'INFO', 2000, 2003, 80, 'Todas'),
    ]
    
    # ========================================
    # SUPLETIVO (1971-1996) - Ensino de 1º e 2º Graus
    # ========================================
    disciplinas_supletivo = [
        ('Comunicação em Língua Portuguesa', 'COMPLP', 1971, 1996, 120, 'Supletivo 1º Grau'),
        ('Matemática', 'MAT', 1971, 1996, 120, 'Supletivo'),
        ('Estudos de Problemas Brasileiros', 'EPB', 1971, 1996, 80, 'Supletivo'),
        ('Ciências Físicas e Biológicas', 'CFB', 1971, 1996, 80, 'Supletivo 1º Grau'),
        ('Língua Portuguesa e Literatura Brasileira', 'LPLB', 1971, 1996, 120, 'Supletivo 2º Grau'),
        ('Física e Matemática', 'FISMAT', 1971, 1996, 100, 'Supletivo 2º Grau'),
        ('Química e Biologia', 'QUIBIO', 1971, 1996, 100, 'Supletivo 2º Grau'),
        ('História e Geografia', 'HISTGEO', 1971, 1996, 80, 'Supletivo'),
    ]
    
    # ========================================
    # EJA - Educação de Jovens e Adultos (1996-2003)
    # ========================================
    disciplinas_eja = [
        # EJA Fundamental (Fases I, II, III)
        ('Língua Portuguesa', 'PORT', 1996, 2003, 160, 'EJA Fund'),
        ('Matemática', 'MAT', 1996, 2003, 120, 'EJA Fund'),
        ('Ciências Naturais', 'CNAT', 1996, 2003, 80, 'EJA Fund'),
        ('Estudos da Sociedade e da Natureza', 'ESN', 1996, 2003, 120, 'EJA Fund'),
        
        # EJA Médio (Totalidade I, II, III)
        ('Linguagens e Códigos', 'LINCOD', 1996, 2003, 160, 'EJA Médio'),
        ('Ciências Humanas', 'CHUMANAS', 1996, 2003, 120, 'EJA Médio'),
        ('Ciências da Natureza e Matemática', 'CNATMAT', 1996, 2003, 160, 'EJA Médio'),
    ]
    
    # Combinar todas as listas
    todas_disciplinas = (
        disciplinas_1960_1971 +
        disciplinas_1971_1996 +
        disciplinas_1996_2003 +
        disciplinas_supletivo +
        disciplinas_eja
    )
    
    # Inserir no banco (modalidade_id = 1 para Regular)
    for disciplina in todas_disciplinas:
        cursor.execute('''
            INSERT INTO disciplinas_historicas 
            (nome, codigo, ano_inicio, ano_fim, carga_horaria_padrao, serie, modalidade_id)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        ''', disciplina)

def popular_amparos_legais(cursor):
    """Popula amparos legais do RS e nacionais (1960-2003)"""
    
    amparos = [
        # LDB Nacional
        ('Lei', '4024/61', '1961-12-20', 'LDB - Lei de Diretrizes e Bases da Educação Nacional', 1961, 1971),
        ('Lei', '5692/71', '1971-08-11', 'LDB - Reforma do Ensino de 1º e 2º Graus', 1971, 1996),
        ('Lei', '9394/96', '1996-12-20', 'LDB - Lei de Diretrizes e Bases da Educação Nacional', 1996, None),
        
        # Resoluções RS - EJA
        ('Resolução', '189/87 CEED/RS', '1987-01-01', 'Estabelece normas para Educação de Jovens e Adultos no RS', 1987, 2000),
        ('Parecer', '851/00 CEED/RS', '2000-09-06', 'Diretrizes para reorganização da EJA no RS', 2000, None),
        
        # Pareceres específicos RS
        ('Parecer', '2264/74 CEED/RS', '1974-01-01', 'Programas de Saúde - 1º e 2º Graus', 1974, 1996),
        ('Parecer', '493/76 CEED/RS', '1976-01-01', 'Ensino Religioso - Facultativo', 1976, None),
        ('Parecer', '323/99 CEED/RS', '1999-04-07', 'Reorganização curricular do Ensino Médio', 1999, None),
        
        # Educação Moral e Cívica / OSPB
        ('Decreto-Lei', '869/69', '1969-09-12', 'Torna obrigatória Educação Moral e Cívica', 1969, 1993),
        ('Decreto-Lei', '68065/71', '1971-01-14', 'Estabelece OSPB como disciplina obrigatória', 1971, 1993),
        ('Lei', '8663/93', '1993-06-14', 'Revoga obrigatoriedade de EMC e OSPB', 1993, None),
        
        # Supletivo
        ('Parecer', '699/72 CFE', '1972-07-06', 'Regulamenta Ensino Supletivo', 1972, 1996),
        ('Deliberação', '05/81 CEE/RS', '1981-01-01', 'Normas para Ensino Supletivo no RS', 1981, 1996),
        
        # Ensino Profissionalizante
        ('Lei', '5692/71 Art. 5º', '1971-08-11', 'Habilitações profissionais no 2º Grau', 1971, 1996),
        ('Parecer', '45/72 CFE', '1972-01-12', 'Organização do ensino profissionalizante', 1972, 1996),
        
        # Conclusão de Curso
        ('Resolução', '236/98 CEED/RS', '1998-05-20', 'Certificação de conclusão do Ensino Fundamental', 1998, None),
        ('Resolução', '237/98 CEED/RS', '1998-05-20', 'Certificação de conclusão do Ensino Médio', 1998, None),
    ]
    
    for amparo in amparos:
        cursor.execute('''
            INSERT INTO amparos_legais 
            (tipo, numero, data, descricao, ano_inicio, ano_fim)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', amparo)

def popular_resultados_finais(cursor):
    """Popula códigos de resultados finais"""
    
    resultados = [
        ('A', 'Aprovado'),
        ('AP', 'Aprovado'),
        ('R', 'Reprovado'),
        ('RP', 'Reprovado'),
        ('T', 'Transferido'),
        ('TR', 'Transferido'),
        ('EV', 'Evadido'),
        ('D', 'Desistente'),
        ('AB', 'Abandono'),
        ('AP/DEP', 'Aprovado com Dependência'),
        ('PP', 'Progressão Parcial'),
        ('RF', 'Reprovado por Frequência'),
        ('RCL', 'Reclassificado'),
        ('CUR', 'Cursando'),
        ('APR', 'Aproveitamento de Estudos'),
        ('DISP', 'Dispensado'),
    ]
    
    for resultado in resultados:
        cursor.execute('''
            INSERT INTO resultados_finais (codigo, descricao)
            VALUES (?, ?)
        ''', resultado)

def popular_escola_exemplo(cursor):
    """Adiciona Escola Caetano Gonçalves como exemplo"""
    cursor.execute('''
        INSERT INTO escolas (
            nome, endereco, municipio, estado, telefone,
            decreto_criacao, data_criacao, doe_criacao,
            decreto_reorganizacao, data_reorganizacao, doe_reorganizacao,
            parecer_alteracao, data_alteracao, doe_alteracao,
            entidade_mantenedora, cre, sede_cre, idt
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'Escola Estadual de Ensino Médio Caetano Gonçalves da Silva',
        'Avenida Dom Pedro, 790',
        'Esteio',
        'RS',
        '(51) 3473-1082',
        '8621/58',
        '1958-02-11',
        '1958-02-11',
        '26443/77',
        '1977-12-23',
        '1977-12-23',
        '804/02',
        '2002-07-17',
        '2002-07-29',
        'Governo do Estado do Rio Grande do Sul',
        '27ª',
        'Canoas/RS',
        '6018'
    ))
    
    # Adicionar gestores históricos
    escola_id = cursor.lastrowid
    cursor.execute('''
        INSERT INTO gestores (escola_id, nome, cargo, data_inicio, data_fim, ativo)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (escola_id, 'Maria Santos', 'Diretor', '1990-01-01', '2000-12-31', 0))
    
    cursor.execute('''
        INSERT INTO gestores (escola_id, nome, cargo, data_inicio, ativo)
        VALUES (?, ?, ?, ?, ?)
    ''', (escola_id, 'João da Silva', 'Diretor', '2001-01-01', 1))

if __name__ == '__main__':
    init_db()
