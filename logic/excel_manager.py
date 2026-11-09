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
    """Importa i prodotti da un file Excel nel database SQLite usando openpyxl."""
    if not file_path:
        files_xlsx = glob.glob("*.xlsx")
        if files_xlsx:
            file_path = files_xlsx[0]
        else:
            return False, "Nessun file Excel trovato nella cartella."

    try:
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for row in ws.iter_rows(min_row=2, values_only=True):
            if any(row):
                # Adatta i campi in base alla struttura della tua tabella prodotti
                cursor.execute("""
                    INSERT OR REPLACE INTO prodotti (id, codice_barra, nome, prezzo, giacenza)
                    VALUES (?, ?, ?, ?, ?)
                """, (row[0], row[1], row[2], row[3], row[4]))

        conn.commit()
        conn.close()
        return True, "Importazione completata con successo!"
    except Exception as e:
        return False, str(e)


