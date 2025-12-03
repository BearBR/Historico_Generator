import sqlite3
import shutil
from datetime import datetime
import os

def criar_backup():
    """Cria backup do banco de dados"""
    db_path = 'database/historicos_escolares.db'
    backup_dir = 'database/backups'
    
    # Criar diretório de backups se não existir
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Nome do arquivo de backup com timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f'{backup_dir}/historicos_escolares_{timestamp}.db'
    
    # Copiar arquivo
    shutil.copy2(db_path, backup_path)
    print(f'✅ Backup criado: {backup_path}')
    
    # Manter apenas os últimos 10 backups
    backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')])
    if len(backups) > 10:
        for old_backup in backups[:-10]:
            os.remove(os.path.join(backup_dir, old_backup))
            print(f'🗑️  Backup antigo removido: {old_backup}')
    
    return backup_path

if __name__ == '__main__':
    criar_backup()
