import sqlite3
import time

# Esperar um pouco caso o Flask esteja liberando o arquivo
time.sleep(2)

conn = sqlite3.connect('database/historicos_escolares.db')
cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"📊 Tabelas no banco: {[t[0] for t in tables]}")

# Verificar estrutura da tabela escolas
cursor.execute("PRAGMA table_info(escolas)")
columns = cursor.fetchall()
print(f"\n📋 Colunas da tabela 'escolas':")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Verificar se coluna já existe
column_names = [col[1] for col in columns]
if 'eh_escola_padrao' in column_names:
    print('\n⚠️  Coluna eh_escola_padrao já existe!')
else:
    try:
        cursor.execute('ALTER TABLE escolas ADD COLUMN eh_escola_padrao BOOLEAN DEFAULT 0')
        print('\n✅ Coluna eh_escola_padrao adicionada')
    except sqlite3.OperationalError as e:
        print(f'\n❌ Erro ao adicionar coluna: {e}')

# Atualizar escola Caetano como padrão
cursor.execute("UPDATE escolas SET eh_escola_padrao = 1 WHERE nome LIKE '%CAETANO%'")
affected = cursor.rowcount
print(f'✅ {affected} escola(s) marcada(s) como padrão')

# Verificar escolas
cursor.execute("SELECT id, nome, eh_escola_padrao FROM escolas")
escolas = cursor.fetchall()
print(f"\n📚 Escolas cadastradas:")
for escola in escolas:
    padrao = "✓ PADRÃO" if escola[2] else ""
    print(f"  - [{escola[0]}] {escola[1]} {padrao}")

conn.commit()
conn.close()
print('\n✅ Migração concluída!')
