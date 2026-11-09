import os
import sqlite3

# Trova sempre la cartella assoluta in cui si trova questo file, 
# azzerando qualsiasi problema legato alla directory di avvio del terminale.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'cassa.db')

def get_db_connection():
    # Assicura che la cartella database esista
    os.makedirs(os.path.join(BASE_DIR, 'database'), exist_ok=True)
    return sqlite3.connect(DB_PATH)
