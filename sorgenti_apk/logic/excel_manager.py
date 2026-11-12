import sqlite3
import openpyxl
import glob
import os

DB_PATH = "database/magazzino.db" if os.path.exists("database/magazzino.db") else "magazzino.db"

def esporta_magazzino_excel(file_path="export_magazzino.xlsx"):
    """Esporta i prodotti dal database SQLite a un file Excel usando openpyxl."""
    try:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Magazzino"

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM prodotti")
        rows = cursor.fetchall()
        
        column_names = [description[0] for description in cursor.description]
        
        # Verifica le colonne esistenti nella tabella prodotti
        cursor.execute("PRAGMA table_info(prodotti)")
        colonne = [col[1] for col in cursor.fetchall()]
        
        # Se la tabella esiste ma manca codice_barra, la aggiungiamo
        if colonne and 'codice_barra' not in colonne:
            cursor.execute("ALTER TABLE prodotti ADD COLUMN codice_barra TEXT")
            conn.commit()
        conn.close()

        ws.append(column_names)
        for row in rows:
            ws.append(row)

        wb.save(file_path)
        return True, "Esportazione completata con successo!"
    except Exception as e:
        return False, str(e)




def importa_magazzino_excel(file_path=None):
    import sqlite3, os, pandas as pd
    try:
        if not file_path:
            file_path = os.path.abspath("dati_excel/export_magazzino.xlsx")
        
        if not os.path.exists(file_path):
            return False, f"File non trovato: {file_path}"
            
        df = pd.read_excel(file_path) if file_path.endswith((".xlsx", ".xls")) else pd.read_csv(file_path)
        
        db_path = os.path.abspath("cassa.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Creiamo la tabella prodotti se non esiste
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prodotti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                COALESCE(barcode, codice, codice_barre, ean, '') TEXT,
                nome TEXT,
                prezzo REAL,
                giacenza REAL,
                categoria TEXT
            )
        ''')
        
        # Verifichiamo le colonne reali della tabella SQLite
        cursor.execute("PRAGMA table_info(prodotti)")
        colonne_db = [col[1] for col in cursor.fetchall()]
        
        # Inseriamo riga per riga mappando in modo flessibile
        righe_caricate = 0
        for _, row in df.iterrows():
            # Troviamo i valori mappando le colonne del DataFrame
            COALESCE(barcode, codice, codice_barre, ean, '')_val = str(row.get("Barcode", row.get("codice_barra", row.get("Codice", ""))))
            nome_val = str(row.get("Nome", row.get("Prodotto", row.get("Articolo", ""))))
            
            try:
                prezzo_val = float(row.get("Prezzo", row.get("Prezzo Vendita", 0.0)))
            except:
                prezzo_val = 0.0
                
            try:
                giacenza_val = float(row.get("Giacenza", row.get("Quantita", 0)))
            except:
                giacenza_val = 0.0
                
            categoria_val = str(row.get("Categoria", ""))
            
            # Inserimento dinamico in base alle colonne effettive presenti nel DB
            if "codice_barra" in colonne_db and "COALESCE(barcode, codice, codice_barre, ean, '')" in colonne_db:
                cursor.execute("INSERT INTO prodotti (COALESCE(barcode, codice, codice_barre, ean, ''), codice_barra, nome, prezzo, giacenza, categoria) VALUES (?, ?, ?, ?, ?, ?)",
                               (COALESCE(barcode, codice, codice_barre, ean, '')_val, COALESCE(barcode, codice, codice_barre, ean, '')_val, nome_val, prezzo_val, giacenza_val, categoria_val))
            elif "codice_barra" in colonne_db:
                cursor.execute("INSERT INTO prodotti (codice_barra, nome, prezzo, giacenza, categoria) VALUES (?, ?, ?, ?, ?)",
                               (COALESCE(barcode, codice, codice_barre, ean, '')_val, nome_val, prezzo_val, giacenza_val, categoria_val))
            elif "COALESCE(barcode, codice, codice_barre, ean, '')" in colonne_db:
                cursor.execute("INSERT INTO prodotti (COALESCE(barcode, codice, codice_barre, ean, ''), nome, prezzo, giacenza, categoria) VALUES (?, ?, ?, ?, ?)",
                               (COALESCE(barcode, codice, codice_barre, ean, '')_val, nome_val, prezzo_val, giacenza_val, categoria_val))
            else:
                cursor.execute("INSERT INTO prodotti (nome, prezzo, giacenza, categoria) VALUES (?, ?, ?, ?)",
                               (nome_val, prezzo_val, giacenza_val, categoria_val))
            righe_caricate += 1
            
        conn.commit()
        conn.close()
        return True, f"Importazione completata con successo! Righe caricate: {righe_caricate}"
    except Exception as e:
        return False, str(e)
