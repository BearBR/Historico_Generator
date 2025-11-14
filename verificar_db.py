import sqlite3

conn = sqlite3.connect('database/historicos_escolares.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM disciplinas_historicas')
total = cursor.fetchone()[0]
print(f'Total de disciplinas: {total}')

if total > 0:
    print('\nPrimeiras 10 disciplinas:')
    cursor.execute('SELECT id, nome, codigo, ano_inicio, ano_fim FROM disciplinas_historicas LIMIT 10')
    for row in cursor.fetchall():
        print(f'  ID: {row[0]}, Nome: {row[1]}, Código: {row[2]}, Período: {row[3]}-{row[4]}')
else:
    print('\n⚠️ Nenhuma disciplina encontrada no banco!')

conn.close()
