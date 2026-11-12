# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
import sqlite3
import os

class InterfacciaMagazzino(Screen):
    def __init__(self, **kwargs):
        super(InterfacciaMagazzino, self).__init__(**kwargs)
        self.articolo_selezionato = None
        self.item_da_eliminare = None

        root = BoxLayout(orientation="vertical", spacing=0)

        # 1. Tab superiori di navigazione
        top_tabs = BoxLayout(size_hint_y=None, height=45, spacing=2)
        btn_tab_cassa = Button(text="Cassa / Vendita", background_color=(0.2, 0.1, 0.5, 1))
        btn_tab_mag = Button(text="Magazzino", background_color=(0.8, 0.8, 0.8, 1), color=(0,0,0,1))
        btn_tab_storico = Button(text="Chiusura & Storico", background_color=(0.2, 0.1, 0.5, 1))
        top_tabs.add_widget(btn_tab_cassa)
        top_tabs.add_widget(btn_tab_mag)
        top_tabs.add_widget(btn_tab_storico)
        root.add_widget(top_tabs)

        # 2. Barra Gestione Magazzino (Stile Odoo)
        odoo_bar = BoxLayout(size_hint_y=None, height=50, padding=5, spacing=10)
        lbl_title = Label(text="Gestione Magazzino (Stile Odoo)", bold=True, color=(0,0,0,1), size_hint_x=1.5)
        
        btn_elenco = Button(text="Elenco", background_color=(0.1, 0.4, 0.7, 1))
        btn_griglia = Button(text="Vista Griglia", background_color=(0.2, 0.2, 0.2, 1))
        btn_esporta = Button(text="Esporta Excel", background_color=(0.1, 0.6, 0.2, 1))
        btn_importa = Button(text="Importa Excel", background_color=(0.1, 0.3, 0.8, 1))
        btn_importa.bind(on_press=self.importa_excel)
        btn_allerta = Button(text="⚠ Allerta", background_color=(0.6, 0.2, 0.2, 1))

        odoo_bar.add_widget(lbl_title)
        odoo_bar.add_widget(btn_elenco)
        odoo_bar.add_widget(btn_griglia)
        odoo_bar.add_widget(btn_esporta)
        odoo_bar.add_widget(btn_importa)
        odoo_bar.add_widget(btn_allerta)
        root.add_widget(odoo_bar)

        # 3. Barra di ricerca e filtri rapidi
        filter_bar = BoxLayout(size_hint_y=None, height=40, spacing=10, padding=5)
        self.search_input = TextInput(hint_text="Cerca per nome o codice...", multiline=False, size_hint_x=2)
        btn_raggruppa = Button(text="Raggruppa per...", background_color=(0.3, 0.3, 0.3, 1))
        btn_tutti = Button(text="Sel. Tutti", background_color=(0.3, 0.3, 0.3, 1))
        btn_desel = Button(text="Deselez.", background_color=(0.3, 0.3, 0.3, 1))

        filter_bar.add_widget(self.search_input)
        filter_bar.add_widget(btn_raggruppa)
        filter_bar.add_widget(btn_tutti)
        filter_bar.add_widget(btn_desel)
        root.add_widget(filter_bar)

        # 4. Area Centrale (Tabella a sinistra + Dettagli a destra)
        center_area = BoxLayout(orientation="horizontal", spacing=10, padding=5)

        # Sinistra: Lista articoli
        left_box = BoxLayout(orientation="vertical", spacing=5)
        lbl_header_list = Label(text="Elenco Articoli (Tutti / Seleziona)", size_hint_y=None, height=30, bold=True, color=(0,0,0,1))
        left_box.add_widget(lbl_header_list)

        self.list_scroll = ScrollView()
        self.list_content = GridLayout(cols=1, spacing=3, size_hint_y=None)
        self.list_content.bind(minimum_height=self.list_content.setter("height"))
        self.list_scroll.add_widget(self.list_content)
        left_box.add_widget(self.list_scroll)
        center_area.add_widget(left_box)

        # Destra: Modulo dettagli articolo (Stile Odoo / Campi completi)
        right_box = GridLayout(cols=2, spacing=8, size_hint_x=1.3, padding=5)

        right_box.add_widget(Label(text="Nome Prodotto:", color=(0,0,0,1)))
        self.txt_nome = TextInput(multiline=False)
        right_box.add_widget(self.txt_nome)

        right_box.add_widget(Label(text="Codice a barre (EAN):", color=(0,0,0,1)))
        self.txt_barcode = TextInput(multiline=False)
        right_box.add_widget(self.txt_barcode)

        right_box.add_widget(Label(text="Categoria:", color=(0,0,0,1)))
        self.txt_categoria = TextInput(multiline=False, hint_text="Seleziona o scrivi...")
        right_box.add_widget(self.txt_categoria)

        right_box.add_widget(Label(text="Lotto:", color=(0,0,0,1)))
        self.txt_lotto = TextInput(multiline=False, hint_text="Seleziona o scrivi...")
        right_box.add_widget(self.txt_lotto)

        right_box.add_widget(Label(text="Scadenza (YYYY-MM-DD):", color=(0,0,0,1)))
        self.txt_scadenza = TextInput(multiline=False)
        right_box.add_widget(self.txt_scadenza)

        right_box.add_widget(Label(text="Prezzo di Vendita (CHF):", color=(0,0,0,1)))
        self.txt_prezzo = TextInput(text="0.0", multiline=False)
        right_box.add_widget(self.txt_prezzo)

        right_box.add_widget(Label(text="Giacenza Fisica:", color=(0,0,0,1)))
        self.txt_giacenza = TextInput(text="0.0", multiline=False)
        right_box.add_widget(self.txt_giacenza)

        right_box.add_widget(Label(text="Colore Pulsante (Hex):", color=(0,0,0,1)))
        self.txt_colore = TextInput(text="#333333", multiline=False)
        right_box.add_widget(self.txt_colore)

        center_area.add_widget(right_box)
        root.add_widget(center_area)

        # 5. Barra Inferiore Pulsanti Azione
        bottom_bar = BoxLayout(size_hint_y=None, height=55, spacing=10, padding=5)
        btn_salva = Button(text="Salva Modifiche / Nuovo", background_color=(0.1, 0.5, 0.8, 1))
        btn_elimina = Button(text="Elimina Selezionati / Corrente", background_color=(0.8, 0.2, 0.2, 1))
        
        bottom_bar.add_widget(btn_salva)
        bottom_bar.add_widget(btn_elimina)
        root.add_widget(bottom_bar)

        self.add_widget(root)

    def on_enter(self, *args):
        self.carica_dati()

    def carica_dati(self, *args):
        self.list_content.clear_widgets()
        try:
            db_path = "dati_excel/magazzino.db"
            if not os.path.exists(db_path):
                db_path = "magazzino.db"
            
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [t[0] for t in cursor.fetchall()]
                target_table = "articoli" if "articoli" in tables else (tables[0] if tables else None)
                
                if target_table:
                    cursor.execute(f"SELECT * FROM {target_table}")
                    rows = cursor.fetchall()
                    for row in rows:
                        txt = " | ".join(str(val) for val in row[:5])
                        lbl = Label(text=txt, size_hint_y=None, height=35, color=(0,0,0,1))
                        self.list_content.add_widget(lbl)
                conn.close()
            else:
                self.list_content.add_widget(Label(text="Nessun database trovato. Clicca 'Importa Excel'.", color=(0,0,0,1), size_hint_y=None, height=35))
        except Exception as e:
            print(f"Errore caricamento: {e}")

    def importa_excel(self, *args):
        try:
            import pandas as pd
            excel_path = "dati_excel/listino.xlsx"
            if os.path.exists(excel_path):
                df = pd.read_excel(excel_path)
                os.makedirs("dati_excel", exist_ok=True)
                conn = sqlite3.connect("dati_excel/magazzino.db")
                df.to_sql("articoli", conn, if_exists="replace", index=False)
                conn.close()
                self.carica_dati()
        except Exception as e:
            print(f"Errore importazione: {e}")

    def aggiorna_selezione_chk(self, item_id, active):
        pass

    def seleziona_articolo(self, item_id):
        self.articolo_selezionato = item_id

    def gestisci_eliminazione_articolo(self, *args):
        return True
