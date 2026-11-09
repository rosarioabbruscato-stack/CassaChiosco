import sqlite3
import os

DB_PATH = "database/negozio.db"

def init_db():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prodotti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codice_barra TEXT UNIQUE,
            nome TEXT NOT NULL,
            categoria TEXT,
            categoria_pos TEXT,
            prezzo REAL DEFAULT 0.0,
            giacenza REAL DEFAULT 0.0,
            gestisce_lotti INTEGER DEFAULT 0,
            lotto TEXT,
            data_scadenza TEXT,
            gestione_scadenza TEXT,
            colore_pulsante TEXT DEFAULT '#333333',
            foto_path TEXT
        )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
