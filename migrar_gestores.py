"""
Script de migração para atualizar a tabela gestores
Permite data_inicio como NULL
"""
import sqlite3

db_path = 'database/historicos_escolares.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Desabilitar foreign keys temporariamente
    cursor.execute('PRAGMA foreign_keys=OFF')
    
    # Criar nova tabela com estrutura atualizada
    cursor.execute('''
        CREATE TABLE gestores_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            escola_id INTEGER NOT NULL,
            nome VARCHAR(200) NOT NULL,
            cargo VARCHAR(100) NOT NULL,
            data_inicio DATE,
            data_fim DATE,
            ativo BOOLEAN DEFAULT 1,
            FOREIGN KEY(escola_id) REFERENCES escolas(id)
        )
    ''')
    
    # Copiar dados da tabela antiga para a nova
    cursor.execute('INSERT INTO gestores_new SELECT * FROM gestores')
    
    # Remover tabela antiga
    cursor.execute('DROP TABLE gestores')
    
    # Renomear nova tabela
    cursor.execute('ALTER TABLE gestores_new RENAME TO gestores')
    
    # Reabilitar foreign keys
    cursor.execute('PRAGMA foreign_keys=ON')
    
    conn.commit()
    print('✅ Tabela gestores atualizada com sucesso!')
    print('   data_inicio agora permite valores NULL')
    
except Exception as e:
    conn.rollback()
    print(f'❌ Erro ao migrar tabela: {e}')
    
finally:
    conn.close()
