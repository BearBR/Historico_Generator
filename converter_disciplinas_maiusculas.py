"""
Script para converter nomes de todas as disciplinas para CAIXA ALTA
"""
import sqlite3
import os

def converter_disciplinas_maiusculas():
    db_path = 'database/historico.db'
    
    if not os.path.exists(db_path):
        print(f'❌ Banco de dados não encontrado: {db_path}')
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Buscar todas as disciplinas
    cursor.execute('SELECT id, nome FROM disciplinas_historicas')
    disciplinas = cursor.fetchall()
    
    print(f'Total de disciplinas encontradas: {len(disciplinas)}')
    print('-' * 60)
    
    convertidas = 0
    
    for disc_id, nome in disciplinas:
        nome_upper = nome.upper()
        
        if nome != nome_upper:
            print(f'Convertendo: "{nome}" → "{nome_upper}"')
            cursor.execute('UPDATE disciplinas_historicas SET nome = ? WHERE id = ?', (nome_upper, disc_id))
            convertidas += 1
        else:
            print(f'Já está OK: "{nome}"')
    
    conn.commit()
    conn.close()
    
    print('-' * 60)
    if convertidas > 0:
        print(f'✅ Concluído!')
        print(f'Total convertidas: {convertidas}')
        print(f'Total já em maiúsculas: {len(disciplinas) - convertidas}')
    else:
        print(f'✅ Todas as disciplinas já estão em MAIÚSCULAS!')

if __name__ == '__main__':
    print('=' * 60)
    print('CONVERTER DISCIPLINAS PARA CAIXA ALTA')
    print('=' * 60)
    print()
    
    resposta = input('Deseja converter TODAS as disciplinas para MAIÚSCULAS? (S/N): ')
    
    if resposta.upper() == 'S':
        converter_disciplinas_maiusculas()
    else:
        print('Operação cancelada.')
