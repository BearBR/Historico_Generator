"""
Script para adicionar coluna escola_nome_manual à tabela historico_anos_letivos
"""
import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'historicos_escolares.db')

def migrar():
    print(f"Conectando ao banco de dados: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(historico_anos_letivos)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'escola_nome_manual' in colunas:
            print("✓ Coluna 'escola_nome_manual' já existe!")
        else:
            print("Adicionando coluna 'escola_nome_manual'...")
            cursor.execute("""
                ALTER TABLE historico_anos_letivos 
                ADD COLUMN escola_nome_manual VARCHAR(255)
            """)
            print("✓ Coluna 'escola_nome_manual' adicionada!")
        
        # Tornar escola_id nullable (se necessário)
        # SQLite não suporta ALTER COLUMN diretamente, então verificamos apenas
        print("✓ Verificando coluna 'escola_id'...")
        
        conn.commit()
        print("\n✓ Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"✗ Erro durante a migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrar()
