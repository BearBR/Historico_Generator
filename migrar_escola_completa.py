"""
Script para adicionar colunas escola_municipio_manual e escola_estado_manual
à tabela historico_anos_letivos
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
        # Verificar se as colunas já existem
        cursor.execute("PRAGMA table_info(historico_anos_letivos)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'escola_municipio_manual' in colunas:
            print("✓ Coluna 'escola_municipio_manual' já existe!")
        else:
            print("Adicionando coluna 'escola_municipio_manual'...")
            cursor.execute("""
                ALTER TABLE historico_anos_letivos 
                ADD COLUMN escola_municipio_manual VARCHAR(100)
            """)
            print("✓ Coluna 'escola_municipio_manual' adicionada!")
        
        if 'escola_estado_manual' in colunas:
            print("✓ Coluna 'escola_estado_manual' já existe!")
        else:
            print("Adicionando coluna 'escola_estado_manual'...")
            cursor.execute("""
                ALTER TABLE historico_anos_letivos 
                ADD COLUMN escola_estado_manual VARCHAR(2)
            """)
            print("✓ Coluna 'escola_estado_manual' adicionada!")
        
        conn.commit()
        print("\n✓ Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"✗ Erro durante a migração: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrar()
