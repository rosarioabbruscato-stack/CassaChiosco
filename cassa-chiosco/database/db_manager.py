import sqlite3
import os
from core.config import DB_PATH

class DatabaseManager:
    def __init__(self):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(DB_PATH)

    def init_db(self):
        """Crea le tabelle iniziali se non esistono."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prodotti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codice TEXT UNIQUE,
                nome TEXT,
                prezzo REAL
            )
        """)
        conn.commit()
        conn.close()

    def esegui_query(self, query, parametri=()):
        """Esegue query di scrittura/aggiornamento in modo sicuro."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, parametri)
        conn.commit()
        conn.close()

    def recupera_dati(self, query, parametri=()):
        """Esegue query di sola lettura."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, parametri)
        risultati = cursor.fetchall()
        conn.close()
        return risultati
