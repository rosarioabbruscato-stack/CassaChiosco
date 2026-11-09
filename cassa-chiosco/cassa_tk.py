import tkinter as tk
import sqlite3
import os

root = tk.Tk()
root.title("CassaChiosco - Modalità Emergenza Tkinter")
root.geometry("1024x768")

# Connessione al database esistente
db_path = "database/negozio.db"
os.makedirs("database", exist_ok=True)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Etichetta di stato
label_titolo = tk.Label(root, text="CassaChiosco - Operatore: Rosario Vincenzo", font=("Arial", 18, "bold"))
label_titolo.pack(pady=20)

label_info = tk.Label(root, text="Interfaccia di emergenza attiva sul database locale.", font=("Arial", 12))
label_info.pack(pady=10)

def chiudi_cassa():
    conn.close()
    root.destroy()

btn_chiudi = tk.Button(root, text="Chiudi Cassa", font=("Arial", 14), bg="red", fg="white", command=chiudi_cassa)
btn_chiudi.pack(side=tk.BOTTOM, pady=30)

root.mainloop()
