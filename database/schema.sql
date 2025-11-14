-- Schema do Sistema de Históricos Escolares
-- Data: 2025

-- ============================================
-- TABELA: ESCOLAS
-- ============================================
CREATE TABLE IF NOT EXISTS escolas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    endereco TEXT NOT NULL,
    municipio TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'RS',
    telefone TEXT,
    
    -- Decretos e Documentos
    decreto_criacao TEXT,
    data_criacao DATE,
    doe_criacao DATE,
    
    decreto_reorganizacao TEXT,
    data_reorganizacao DATE,
    doe_reorganizacao DATE,
    
    parecer_alteracao TEXT,
    data_alteracao DATE,
    doe_alteracao DATE,
    
    -- Informações Administrativas
    entidade_mantenedora TEXT,
    cre TEXT,  -- Coordenadoria Regional de Educação
    sede_cre TEXT,
    idt TEXT,  -- Identificador da escola
    
    -- Logo da Escola
    logo TEXT,  -- Caminho da imagem
    
    -- Controle
    ativa BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABELA: MODALIDADES DE ENSINO
-- ============================================
CREATE TABLE IF NOT EXISTS modalidades_ensino (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,  -- Regular, Supletivo, EJA
    descricao TEXT,
    ano_inicio INTEGER,
    ano_fim INTEGER,
    ativa BOOLEAN DEFAULT 1
);

-- ============================================
-- TABELA: DISCIPLINAS HISTÓRICAS
-- ============================================
CREATE TABLE IF NOT EXISTS disciplinas_historicas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    codigo TEXT,
    ano_inicio INTEGER NOT NULL,
    ano_fim INTEGER,
    carga_horaria_padrao INTEGER,  -- Carga horária padrão em horas
    serie TEXT,  -- Qual série/ano era ministrada
    modalidade_id INTEGER,
    ativa BOOLEAN DEFAULT 1,
    
    FOREIGN KEY (modalidade_id) REFERENCES modalidades_ensino(id)
);

-- ============================================
-- TABELA: AMPAROS LEGAIS
-- ============================================
CREATE TABLE IF NOT EXISTS amparos_legais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,  -- Lei, Decreto, Resolução, Parecer
    numero TEXT NOT NULL,
    data DATE,
    descricao TEXT,
    ano_inicio INTEGER,
    ano_fim INTEGER,
    ativo BOOLEAN DEFAULT 1
);

-- ============================================
-- TABELA: RESULTADOS FINAIS
-- ============================================
CREATE TABLE IF NOT EXISTS resultados_finais (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,  -- AP, RP, EX, DI, TR, etc.
    descricao TEXT NOT NULL,
    tipo TEXT,  -- aprovado, reprovado, transferido, etc.
    ano_inicio INTEGER,
    ano_fim INTEGER,
    ativo BOOLEAN DEFAULT 1
);

-- ============================================
-- TABELA: ALUNOS
-- ============================================
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_completo TEXT NOT NULL,
    data_nascimento DATE NOT NULL,
    naturalidade TEXT,
    uf_nascimento TEXT,
    cpf TEXT UNIQUE,
    rg TEXT,
    orgao_emissor TEXT,
    uf_rg TEXT,
    
    -- Filiação
    nome_mae TEXT,
    nome_pai TEXT,
    
    -- Endereço
    endereco TEXT,
    municipio TEXT,
    estado TEXT,
    cep TEXT,
    telefone TEXT,
    email TEXT,
    
    -- Controle
    ativo BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABELA: GESTORES
-- ============================================
CREATE TABLE IF NOT EXISTS gestores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    escola_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    cargo TEXT NOT NULL,  -- Diretor, Vice-Diretor, Secretário
    data_inicio DATE NOT NULL,
    data_fim DATE,
    ativo BOOLEAN DEFAULT 1,
    
    FOREIGN KEY (escola_id) REFERENCES escolas(id)
);

-- ============================================
-- TABELA: HISTÓRICOS
-- ============================================
CREATE TABLE IF NOT EXISTS historicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL,
    escola_id INTEGER NOT NULL,
    
    -- Informações do Histórico
    ano INTEGER NOT NULL,
    serie TEXT NOT NULL,  -- 1ª Série, 2ª Série, etc.
    modalidade_id INTEGER NOT NULL,
    nivel TEXT,  -- Fundamental, Médio
    
    -- Datas
    data_inicio DATE,
    data_termino DATE,
    
    -- Escola de Origem (caso seja transferência)
    escola_origem TEXT,
    municipio_origem TEXT,
    uf_origem TEXT,
    
    -- Resultado Final
    resultado_final_id INTEGER,
    
    -- Dias Letivos e Carga Horária
    dias_letivos INTEGER,
    carga_horaria_total INTEGER,
    
    -- Observações
    observacoes TEXT,
    
    -- Amparo Legal
    amparo_legal_id INTEGER,
    
    -- Conclusão de Curso
    conclusao_curso BOOLEAN DEFAULT 0,
    data_conclusao DATE,
    amparo_conclusao_id INTEGER,
    numero_certificado TEXT,
    livro_registro TEXT,
    folha_registro TEXT,
    observacoes_conclusao TEXT,
    
    -- Assinaturas
    nome_diretor TEXT,
    nome_secretario TEXT,
    data_emissao DATE,
    
    -- Controle
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (aluno_id) REFERENCES alunos(id),
    FOREIGN KEY (escola_id) REFERENCES escolas(id),
    FOREIGN KEY (modalidade_id) REFERENCES modalidades_ensino(id),
    FOREIGN KEY (resultado_final_id) REFERENCES resultados_finais(id),
    FOREIGN KEY (amparo_legal_id) REFERENCES amparos_legais(id),
    FOREIGN KEY (amparo_conclusao_id) REFERENCES amparos_legais(id)
);

-- ============================================
-- TABELA: HISTÓRICO DISCIPLINAS (Notas e Frequência)
-- ============================================
CREATE TABLE IF NOT EXISTS historico_disciplinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    historico_id INTEGER NOT NULL,
    disciplina_historica_id INTEGER NOT NULL,
    
    -- Nota Final Anual
    nota_final REAL,
    
    -- Frequência
    carga_horaria INTEGER,  -- CH da disciplina
    faltas INTEGER DEFAULT 0,
    frequencia REAL,  -- Calculado automaticamente (percentual)
    
    -- Resultado
    resultado TEXT,  -- A, R, T, EV, D, etc.
    
    FOREIGN KEY (historico_id) REFERENCES historicos(id) ON DELETE CASCADE,
    FOREIGN KEY (disciplina_historica_id) REFERENCES disciplinas_historicas(id)
);

-- ============================================
-- ÍNDICES PARA MELHOR PERFORMANCE
-- ============================================
CREATE INDEX IF NOT EXISTS idx_alunos_cpf ON alunos(cpf);
CREATE INDEX IF NOT EXISTS idx_alunos_nome ON alunos(nome_completo);
CREATE INDEX IF NOT EXISTS idx_historicos_aluno ON historicos(aluno_id);
CREATE INDEX IF NOT EXISTS idx_historicos_escola ON historicos(escola_id);
CREATE INDEX IF NOT EXISTS idx_historicos_ano ON historicos(ano);
CREATE INDEX IF NOT EXISTS idx_gestores_escola ON gestores(escola_id);
CREATE INDEX IF NOT EXISTS idx_disciplinas_ano ON disciplinas_historicas(ano_inicio, ano_fim);

-- ============================================
-- TRIGGERS PARA ATUALIZAR updated_at
-- ============================================
CREATE TRIGGER IF NOT EXISTS update_escolas_timestamp 
AFTER UPDATE ON escolas
BEGIN
    UPDATE escolas SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_alunos_timestamp 
AFTER UPDATE ON alunos
BEGIN
    UPDATE alunos SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS update_historicos_timestamp 
AFTER UPDATE ON historicos
BEGIN
    UPDATE historicos SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
