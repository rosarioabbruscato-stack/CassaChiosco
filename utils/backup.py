import shutil
import os
from datetime import datetime

def esegui_backup_database():
    """
    Crea una copia di sicurezza del database SQLite nella cartella backups/
    preservando lo storico e i dati di cassa durante gli aggiornamenti.
    """
    db_sorgente = "database/cassa.db"
    dir_backup = "database/backups"
    
    if not os.path.exists(db_sorgente):
        print("Nessun database da archiviare trovato.")
        return False
        
    if not os.path.exists(dir_backup):
        os.makedirs(dir_backup)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_destinazione = os.path.join(dir_backup, f"cassa_backup_{timestamp}.db")
    
    try:
        shutil.copy2(db_sorgente, db_destinazione)
        print(f"Backup del database eseguito con successo: {db_destinazione}")
        return db_destinazione
    except Exception as e:
        print(f"Errore durante il backup del database: {e}")
        return None
