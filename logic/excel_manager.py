# -*- coding: utf-8 -*-
import os
try:
    import pandas as pd
except ImportError:
    pd = None

def esporta_magazzino_excel(articoli, filepath):
    if pd is not None and filepath.endswith((".xlsx", ".xls")):
        pd.DataFrame(articoli).to_excel(filepath, index=False)
    else:
        import csv
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(["Nome", "Barcode", "Categoria", "Lotto", "Scadenza", "Prezzo", "Giacenza", "POS", "Colore"])
            for a in articoli:
                w.writerow([
                    a.get("nome", ""),
                    a.get("barcode", ""),
                    a.get("cat", ""),
                    a.get("lotto", ""),
                    a.get("scad", ""),
                    a.get("prezzo", 0.0),
                    a.get("giac", 0.0),
                    a.get("pos", ""),
                    a.get("colore", "")
                ])

def importa_magazzino_excel(filepath):
    articoli = []
    if not os.path.exists(filepath):
        return articoli
    if filepath.endswith((".xlsx", ".xls")) and pd is not None:
        xls = pd.ExcelFile(filepath)
        df = pd.read_excel(xls, xls.sheet_names[0])
        for _, row in df.iterrows():
            nome = str(row.get("Nome", row.get("nome", "Senza Nome")))
            barcode_val = str(row.get("Barcode", row.get("codice_barra", row.get("Codice", row.get("barcode", "")))))
            if barcode_val == "nan": barcode_val = ""
            prezzo = float(row.get("Prezzo di vendita", row.get("prezzo", 0.0)) or 0.0)
            giac = float(row.get("Quantità giacenza fisica", row.get("giac", 0.0)) or 0.0)
            cat = str(row.get("Etichette", row.get("cat", "N/D")))
            if cat == "nan": cat = "N/D"
            
            articoli.append({
                "nome": nome,
                "barcode": barcode_val,
                "cat": cat,
                "lotto": "N/D",
                "scad": "",
                "prezzo": prezzo,
                "giac": giac,
                "pos": "",
                "colore": "#333333",
                "selezionato": False
            })
    else:
        import csv
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=";")
            next(reader, None)
            for row in reader:
                if len(row) >= 7:
                    articoli.append({
                        "nome": row[0],
                        "barcode": row[1],
                        "cat": row[2],
                        "lotto": row[3],
                        "scad": row[4],
                        "prezzo": float(row[5] or 0.0),
                        "giac": float(row[6] or 0.0),
                        "pos": row[7] if len(row) > 7 else "",
                        "colore": row[8] if len(row) > 8 else "#333333",
                        "selezionato": False
                    })
    return articoli
