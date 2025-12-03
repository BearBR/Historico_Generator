import sqlite3

conn = sqlite3.connect('database/historico.db')
cursor = conn.cursor()

# Listar todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print(f"📊 Tabelas no banco: {[t[0] for t in tables]}")

# Verificar estrutura da tabela escolas (se existir)
try:
    cursor.execute("PRAGMA table_info(escola)")
    columns = cursor.fetchall()
    print(f"\n📋 Colunas da tabela 'escola':")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
except:
    pass

try:
    # Tentar adicionar a coluna
    cursor.execute('ALTER TABLE escola ADD COLUMN eh_escola_padrao BOOLEAN DEFAULT 0')
    print('\n✅ Coluna eh_escola_padrao adicionada')
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e).lower():
        print('\n⚠️  Coluna eh_escola_padrao já existe')
    else:
        print(f'\n❌ Erro: {e}')

# Atualizar escola Caetano como padrão
cursor.execute("UPDATE escola SET eh_escola_padrao = 1 WHERE nome LIKE '%CAETANO%'")
affected = cursor.rowcount
print(f'✅ {affected} escola(s) marcada(s) como padrão')

conn.commit()
conn.close()
print('✅ Migração concluída!')
