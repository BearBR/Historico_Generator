#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de migração para adicionar eh_escola_padrao à tabela escolas
"""

import sqlite3
import os
from pathlib import Path

def migrate():
    """Adiciona coluna eh_escola_padrao à tabela escolas"""
    
    db_path = Path(__file__).parent / 'database' / 'historicos_escolares.db'
    
    if not db_path.exists():
        print(f"❌ Banco de dados não encontrado: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Verificar se coluna já existe
        cursor.execute("PRAGMA table_info(escolas)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'eh_escola_padrao' in columns:
            print("✅ Coluna eh_escola_padrao já existe na tabela escolas")
            conn.close()
            return True
        
        # Adicionar coluna
        print("➕ Adicionando coluna eh_escola_padrao à tabela escolas...")
        cursor.execute("""
            ALTER TABLE escolas 
            ADD COLUMN eh_escola_padrao BOOLEAN DEFAULT 0
        """)
        
        conn.commit()
        print("✅ Migração concluída com sucesso!")
        print("📋 Coluna eh_escola_padrao adicionada com valor padrão FALSE (0)")
        
        conn.close()
        return True
        
    except sqlite3.OperationalError as e:
        print(f"❌ Erro ao executar migração: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

if __name__ == '__main__':
    migrate()
