import sqlite3

conn = sqlite3.connect('database/historicos_escolares.db')
cursor = conn.cursor()

# Buscar aluno
cursor.execute('SELECT id, nome_completo FROM alunos WHERE nome_completo LIKE "%NEI FERNANDO%"')
aluno = cursor.fetchone()
print(f'📋 Aluno: [{aluno[0]}] {aluno[1]}')

# Buscar histórico
cursor.execute('SELECT id FROM historicos WHERE aluno_id = ?', (aluno[0],))
hist = cursor.fetchone()
print(f'📚 Histórico ID: {hist[0]}')

# Buscar anos letivos
cursor.execute('SELECT id, ano, escola_id FROM historico_anos_letivos WHERE historico_id = ?', (hist[0],))
anos = cursor.fetchall()
print(f'\n📅 Anos letivos cadastrados: {len(anos)} anos')
for ano in anos:
    # Buscar disciplinas de cada ano
    cursor.execute('SELECT COUNT(*) FROM historico_ano_disciplinas WHERE ano_letivo_id = ?', (ano[0],))
    disc_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT nome FROM escolas WHERE id = ?', (ano[2],))
    escola_nome = cursor.fetchone()[0]
    
    print(f'\n  ✓ Ano {ano[1]} - {escola_nome}')
    print(f'    Disciplinas: {disc_count}')
    
    if disc_count > 0:
        cursor.execute('''
            SELECT d.nome, d.carga_horaria, had.nota, had.resultado_final_id
            FROM historico_ano_disciplinas had
            JOIN disciplinas_historicas d ON had.disciplina_id = d.id
            WHERE had.ano_letivo_id = ?
        ''', (ano[0],))
        disciplinas = cursor.fetchall()
        for disc in disciplinas:
            print(f'      - {disc[0]}: CH={disc[1]}, Nota={disc[2]}, Resultado={disc[3]}')

conn.close()
