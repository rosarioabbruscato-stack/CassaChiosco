# -*- coding: utf-8 -*-
import os, json, csv
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.graphics import Color, Rectangle
from kivy.app import App

DB_FILE = "magazzino_data.json"

class FileChooserPopup(Popup):
    def __init__(self, callback, mode="open", **kwargs):
        super(FileChooserPopup, self).__init__(**kwargs)
        self.callback = callback
        self.mode = mode
        self.title = "Seleziona file CSV da Importare" if mode == "open" else "Scegli dove Esportare il file CSV"
        self.size_hint = (0.85, 0.85)
        
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        
        self.fc = FileChooserListView(filters=["*.csv"], path=".")
        layout.add_widget(self.fc)
        
        btn_layout = BoxLayout(size_hint_y=None, height=45, spacing=10)
        btn_ok = Button(text="Seleziona", background_normal="", background_color=(0.1, 0.6, 0.3, 1), bold=True)
        btn_ok.bind(on_press=self.conferma)
        
        btn_cancel = Button(text="Annulla", background_normal="", background_color=(0.8, 0.2, 0.2, 1), bold=True)
        btn_cancel.bind(on_press=self.dismiss)
        
        btn_layout.add_widget(btn_ok)
        btn_layout.add_widget(btn_cancel)
        layout.add_widget(btn_layout)
        
        self.content = layout

    def conferma(self, *args):
        selection = self.fc.selection
        if selection:
            path = selection[0]
            self.callback(path)
            self.dismiss()
        elif self.mode == "save" and self.fc.path:
            # Se salvataggio e utente ha selezionato la cartella
            default_path = os.path.join(self.fc.path, "magazzino_export.csv")
            self.callback(default_path)
            self.dismiss()

class InterfacciaMagazzino(Screen):
    def __init__(self, **kwargs):
        super(InterfacciaMagazzino, self).__init__(**kwargs)
        
        self.articoli = self.carica_dati()
        self.articolo_selezionato_idx = None
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        root = BoxLayout(orientation="vertical", spacing=0)

        # 1. Tab superiori di navigazione fissi
        top_tabs = BoxLayout(size_hint_y=None, height=45, spacing=2)
        btn_tab_cassa = Button(text="Cassa / Vendita", background_normal="", background_color=(0.25, 0.25, 0.25, 1), bold=True)
        btn_tab_cassa.bind(on_press=lambda x: self.vai_a("cassa"))
        
        btn_tab_mag = Button(text="Magazzino", background_normal="", background_color=(0.15, 0.1, 0.4, 1), bold=True)
        
        btn_tab_storico = Button(text="Chiusura & Storico", background_normal="", background_color=(0.25, 0.25, 0.25, 1), bold=True)
        btn_tab_storico.bind(on_press=lambda x: self.vai_a("chiusura"))
        
        top_tabs.add_widget(btn_tab_cassa)
        top_tabs.add_widget(btn_tab_mag)
        top_tabs.add_widget(btn_tab_storico)
        root.add_widget(top_tabs)

        # 2. Barra superiore azioni (Stile Odoo) con Esporta/Importa CSV dinamico
        odoo_bar = BoxLayout(size_hint_y=None, height=50, padding=8, spacing=10)
        odoo_bar.add_widget(Label(text="Gestione Magazzino (Stile Odoo)", color=(0.1,0.1,0.1,1), bold=True, font_size=18, halign="left"))
        
        btn_elenco = Button(text="Elenco", size_hint_x=None, width=90, background_normal="", background_color=(0.1, 0.4, 0.6, 1), bold=True)
        btn_griglia = Button(text="Vista Griglia", size_hint_x=None, width=100, background_normal="", background_color=(0.2, 0.2, 0.2, 1), bold=True)
        
        btn_esp_excel = Button(text="Esporta Excel", size_hint_x=None, width=110, background_normal="", background_color=(0.1, 0.6, 0.3, 1), bold=True)
        btn_esp_excel.bind(on_press=lambda x: self.apri_selettore_salvataggio())
        
        btn_imp_excel = Button(text="Importa Excel", size_hint_x=None, width=110, background_normal="", background_color=(0.15, 0.4, 0.7, 1), bold=True)
        btn_imp_excel.bind(on_press=lambda x: self.apri_selettore_apertura())
        
        btn_allerta = Button(text="⚠ Allerta", size_hint_x=None, width=90, background_normal="", background_color=(0.6, 0.1, 0.1, 1), bold=True)
        btn_allerta.bind(on_press=self.filtra_scorte_basse)
        
        odoo_bar.add_widget(btn_elenco)
        odoo_bar.add_widget(btn_griglia)
        odoo_bar.add_widget(btn_esp_excel)
        odoo_bar.add_widget(btn_imp_excel)
        odoo_bar.add_widget(btn_allerta)
        root.add_widget(odoo_bar)

        # 3. Riga di ricerca e filtri
        filter_bar = BoxLayout(size_hint_y=None, height=42, padding=5, spacing=8)
        self.txt_cerca = TextInput(hint_text="Cerca per nome o codice...", multiline=False, size_hint_x=0.5)
        self.txt_cerca.bind(text=self.cerca_articoli)
        
        btn_raggruppa = Button(text="Raggruppa per...", size_hint_x=0.2, background_normal="", background_color=(0.3, 0.3, 0.3, 1))
        btn_sel_tutti = Button(text="Sel. Tutti", size_hint_x=0.15, background_normal="", background_color=(0.3, 0.3, 0.3, 1))
        btn_sel_tutti.bind(on_press=self.seleziona_tutti)
        
        btn_deselez = Button(text="Deselez.", size_hint_x=0.15, background_normal="", background_color=(0.3, 0.3, 0.3, 1))
        btn_deselez.bind(on_press=self.deseleziona_tutti)
        
        filter_bar.add_widget(self.txt_cerca)
        filter_bar.add_widget(btn_raggruppa)
        filter_bar.add_widget(btn_sel_tutti)
        filter_bar.add_widget(btn_deselez)
        root.add_widget(filter_bar)

        # 4. Area Principale Divisa in Due
        main_split = BoxLayout(orientation="horizontal", padding=8, spacing=12)

        # ---- COLONNA SINISTRA: Elenco Articoli ----
        left_layout = BoxLayout(orientation="vertical", spacing=5, size_hint_x=0.5)
        self.lbl_stato_lista = Label(text="Elenco Articoli (Tutti / Seleziona)", color=(0.1,0.1,0.1,1), bold=True, size_hint_y=None, height=25, halign="left")
        left_layout.add_widget(self.lbl_stato_lista)
        
        self.scroll_list = ScrollView()
        self.list_content = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None)
        self.list_content.bind(minimum_height=self.list_content.setter("height"))
        self.scroll_list.add_widget(self.list_content)
        left_layout.add_widget(self.scroll_list)
        main_split.add_widget(left_layout)

        # ---- COLONNA DESTRA: Form Inserimento / Modifica ----
        right_layout = BoxLayout(orientation="vertical", spacing=8, size_hint_x=0.5, padding=5)
        
        row_nome_foto = BoxLayout(size_hint_y=None, height=75, spacing=10)
        box_campi_nome = BoxLayout(orientation="vertical", spacing=3)
        box_campi_nome.add_widget(Label(text="Nome Prodotto:", color=(0.1,0.1,0.1,1), font_size=12, halign="left", size_hint_y=None, height=20))
        self.txt_nome = TextInput(hint_text="Nome prodotto", multiline=False)
        box_campi_nome.add_widget(self.txt_nome)
        row_nome_foto.add_widget(box_campi_nome)
        
        box_foto = BoxLayout(orientation="vertical", size_hint_x=None, width=120)
        box_foto.add_widget(Label(text="Foto Prodotto", color=(0.1,0.1,0.1,1), font_size=11, size_hint_y=None, height=18))
        btn_foto = Button(text="[□ Quadrata\n130 x 130]", background_normal="", background_color=(0.85, 0.85, 0.85, 1), color=(0.4,0.4,0.4,1), font_size=11)
        box_foto.add_widget(btn_foto)
        row_nome_foto.add_widget(box_foto)
        right_layout.add_widget(row_nome_foto)

        box_bc = BoxLayout(orientation="vertical", spacing=3, size_hint_y=None, height=55)
        box_bc.add_widget(Label(text="Codice a barre (EAN):", color=(0.1,0.1,0.1,1), font_size=12, halign="left", size_hint_y=None, height=20))
        self.txt_barcode = TextInput(hint_text="Codice a barre...", multiline=False)
        box_bc.add_widget(self.txt_barcode)
        right_layout.add_widget(box_bc)

        self.txt_cat = self.crea_campo(right_layout, "Categoria:", "Seleziona o scrivi...")
        self.txt_lotto = self.crea_campo(right_layout, "Lotto:", "Seleziona o scrivi...")
        self.txt_scad = self.crea_campo(right_layout, "Scadenza (YYYY-MM-DD):", "YYYY-MM-DD")
        self.txt_prezzo = self.crea_campo(right_layout, "Prezzo di Vendita (CHF):", "0.00")
        self.txt_giac = self.crea_campo(right_layout, "Giacenza Fisica:", "0.0")
        self.txt_pos = self.crea_campo(right_layout, "Categoria POS (Doc. Z):", "Seleziona...")
        self.txt_colore = self.crea_campo(right_layout, "Colore Pulsante (Hex):", "#333333")

        action_row = BoxLayout(size_hint_y=None, height=45, spacing=10, padding=[0, 10, 0, 0])
        btn_salva = Button(text="Salva Modifiche / Nuovo", background_normal="", background_color=(0.1, 0.5, 0.8, 1), bold=True)
        btn_salva.bind(on_press=self.salva_articolo)
        
        btn_elimina = Button(text="Elimina Selezionati / Corrente", background_normal="", background_color=(0.8, 0.2, 0.2, 1), bold=True)
        btn_elimina.bind(on_press=self.elimina_articolo)
        
        action_row.add_widget(btn_salva)
        action_row.add_widget(btn_elimina)
        right_layout.add_widget(action_row)

        main_split.add_widget(right_layout)
        root.add_widget(main_split)
        self.add_widget(root)

        self.aggiorna_lista_video()

    def crea_campo(self, parent, label_text, hint):
        row_f = BoxLayout(size_hint_y=None, height=35, spacing=10)
        lbl = Label(text=label_text, color=(0.1,0.1,0.1,1), font_size=12, size_hint_x=0.45, halign="right")
        lbl.bind(size=lbl.setter("text_size"))
        ti = TextInput(text=hint if hint in ["0.00", "0.0", "#333333"] else "", hint_text=hint if hint not in ["0.00", "0.0", "#333333"] else "", multiline=False, size_hint_x=0.55)
        row_f.add_widget(lbl)
        row_f.add_widget(ti)
        parent.add_widget(row_f)
        return ti

    def carica_dati(self):
        if os.path.exists(DB_FILE):
            try:
                with open(DB_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return [
            {"nome": "Prodotto Test 1", "barcode": "123456", "cat": "Bevande", "lotto": "A1", "scad": "2027-01-01", "prezzo": 5.00, "giac": 10.0, "pos": "Reparto 1", "colore": "#ff5500", "selezionato": False},
            {"nome": "Prodotto Test 2", "barcode": "654321", "cat": "Snack", "lotto": "B2", "scad": "2027-06-01", "prezzo": 3.50, "giac": 25.0, "pos": "Reparto 2", "colore": "#ffdd00", "selezionato": False}
        ]

    def salva_dati(self):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(self.articoli, f, indent=4, ensure_ascii=False)

    def apri_selettore_apertura(self):
        popup = FileChooserPopup(callback=self.importa_csv_file, mode="open")
        popup.open()

    def apri_selettore_salvataggio(self):
        popup = FileChooserPopup(callback=self.esporta_csv_file, mode="save")
        popup.open()

    def esporta_csv_file(self, filepath):
        try:
            with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Nome", "Barcode", "Categoria", "Lotto", "Scadenza", "Prezzo", "Giacenza", "POS", "Colore"])
                for art in self.articoli:
                    writer.writerow([
                        art.get("nome", ""),
                        art.get("barcode", ""),
                        art.get("cat", ""),
                        art.get("lotto", ""),
                        art.get("scad", ""),
                        art.get("prezzo", 0.0),
                        art.get("giac", 0.0),
                        art.get("pos", ""),
                        art.get("colore", "")
                    ])
            self.lbl_stato_lista.text = f"Esportato con successo in: {filepath}"
        except Exception as e:
            self.lbl_stato_lista.text = f"Errore esportazione: {str(e)}"

    def importa_csv_file(self, filepath):
        if not os.path.exists(filepath):
            self.lbl_stato_lista.text = "File selezionato non trovato!"
            return
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f, delimiter=";")
                next(reader, None)
                nuovi_articoli = []
                for row in reader:
                    if len(row) >= 9:
                        nuovi_articoli.append({
                            "nome": row[0],
                            "barcode": row[1],
                            "cat": row[2],
                            "lotto": row[3],
                            "scad": row[4],
                            "prezzo": float(row[5]) if row[5] else 0.0,
                            "giac": float(row[6]) if row[6] else 0.0,
                            "pos": row[7],
                            "colore": row[8],
                            "selezionato": False
                        })
                if nuovi_articoli:
                    self.articoli = nuovi_articoli
                    self.salva_dati()
                    self.aggiorna_lista_video()
                    self.lbl_stato_lista.text = f"Importati {len(nuovi_articoli)} articoli da {os.path.basename(filepath)}!"
                else:
                    self.lbl_stato_lista.text = "Nessun dato valido trovato nel file."
        except Exception as e:
            self.lbl_stato_lista.text = f"Errore importazione: {str(e)}"

    def aggiorna_lista_video(self, filtro=""):
        self.list_content.clear_widgets()
        for idx, art in enumerate(self.articoli):
            if filtro and filtro.lower() not in art["nome"].lower() and filtro.lower() not in art["barcode"].lower():
                continue
            
            row = BoxLayout(size_hint_y=None, height=35, spacing=5)
            
            chk_btn = Button(text="☑" if art.get("selezionato") else "☐", size_hint_x=None, width=30, background_normal="", background_color=(0.9, 0.9, 0.9, 1), color=(0,0,0,1))
            chk_btn.bind(on_press=lambda inst, i=idx: self.toggle_seleziona(i))
            
            txt_riga = f"{art['nome']} | Cat: {art['cat']} | Lotto: {art['lotto']} | CHF {art['prezzo']:.2f} | Giac: {art['giac']}"
            btn_riga = Button(text=txt_riga, background_normal="", background_color=(0.95, 0.95, 0.95, 1), color=(0.1,0.1,0.1,1), font_size=12, halign="left")
            btn_riga.bind(size=btn_riga.setter("text_size"))
            btn_riga.bind(on_press=lambda inst, i=idx: self.carica_articolo_in_form(i))
            
            row.add_widget(chk_btn)
            row.add_widget(btn_riga)
            self.list_content.add_widget(row)

    def toggle_seleziona(self, idx):
        self.articoli[idx]["selezionato"] = not self.articoli[idx].get("selezionato", False)
        self.aggiorna_lista_video(self.txt_cerca.text)

    def seleziona_tutti(self, *args):
        for art in self.articoli:
            art["selezionato"] = True
        self.aggiorna_lista_video(self.txt_cerca.text)

    def deseleziona_tutti(self, *args):
        for art in self.articoli:
            art["selezionato"] = False
        self.aggiorna_lista_video(self.txt_cerca.text)

    def cerca_articoli(self, instance, value):
        self.aggiorna_lista_video(value)

    def filtra_scorte_basse(self, *args):
        self.list_content.clear_widgets()
        for idx, art in enumerate(self.articoli):
            if art["giac"] <= 2.0:
                row = BoxLayout(size_hint_y=None, height=35, spacing=5)
                chk_btn = Button(text="☐", size_hint_x=None, width=30, background_normal="", background_color=(0.9, 0.9, 0.9, 1), color=(0,0,0,1))
                txt_riga = f"[ALLERTA SCORTA] {art['nome']} | Giac: {art['giac']}"
                btn_riga = Button(text=txt_riga, background_normal="", background_color=(1, 0.8, 0.8, 1), color=(0.8,0,0,1), font_size=12, halign="left")
                btn_riga.bind(size=btn_riga.setter("text_size"))
                btn_riga.bind(on_press=lambda inst, i=idx: self.carica_articolo_in_form(i))
                row.add_widget(chk_btn)
                row.add_widget(btn_riga)
                self.list_content.add_widget(row)
        self.lbl_stato_lista.text = "Elenco Articoli (Filtro Scorte Basse)"

    def carica_articolo_in_form(self, idx):
        self.articolo_selezionato_idx = idx
        art = self.articoli[idx]
        self.txt_nome.text = art.get("nome", "")
        self.txt_barcode.text = art.get("barcode", "")
        self.txt_cat.text = art.get("cat", "")
        self.txt_lotto.text = art.get("lotto", "")
        self.txt_scad.text = art.get("scad", "")
        self.txt_prezzo.text = str(art.get("prezzo", 0.00))
        self.txt_giac.text = str(art.get("giac", 0.0))
        self.txt_pos.text = art.get("pos", "")
        self.txt_colore.text = art.get("colore", "#333333")

    def salva_articolo(self, *args):
        try:
            p_val = float(self.txt_prezzo.text.replace(",", ".")) if self.txt_prezzo.text.strip() else 0.0
            g_val = float(self.txt_giac.text.replace(",", ".")) if self.txt_giac.text.strip() else 0.0
        except ValueError:
            p_val, g_val = 0.0, 0.0

        nuovo_art = {
            "nome": self.txt_nome.text.strip() or "Senza Nome",
            "barcode": self.txt_barcode.text.strip(),
            "cat": self.txt_cat.text.strip() or "N/D",
            "lotto": self.txt_lotto.text.strip() or "N/D",
            "scad": self.txt_scad.text.strip(),
            "prezzo": p_val,
            "giac": g_val,
            "pos": self.txt_pos.text.strip(),
            "colore": self.txt_colore.text.strip() or "#333333",
            "selezionato": False
        }

        if self.articolo_selezionato_idx is not None and self.articolo_selezionato_idx < len(self.articoli):
            self.articoli[self.articolo_selezionato_idx] = nuovo_art
        else:
            self.articoli.append(nuovo_art)

        self.salva_dati()
        self.aggiorna_lista_video()
        self.pulisci_form()
        self.lbl_stato_lista.text = "Articolo salvato!"

    def elimina_articolo(self, *args):
        nuovi = [art for art in self.articoli if not art.get("selezionato", False)]
        if len(nuovi) == len(self.articoli) and self.articolo_selezionato_idx is not None:
            if self.articolo_selezionato_idx < len(self.articoli):
                del self.articoli[self.articolo_selezionato_idx]
        else:
            self.articoli = nuovi

        self.articolo_selezionato_idx = None
        self.salva_dati()
        self.aggiorna_lista_video()
        self.pulisci_form()
        self.lbl_stato_lista.text = "Articolo/i eliminato/i!"

    def pulisci_form(self):
        self.txt_nome.text = ""
        self.txt_barcode.text = ""
        self.txt_cat.text = ""
        self.txt_lotto.text = ""
        self.txt_scad.text = ""
        self.txt_prezzo.text = "0.00"
        self.txt_giac.text = "0.0"
        self.txt_pos.text = ""
        self.txt_colore.text = "#333333"
        self.articolo_selezionato_idx = None

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def vai_a(self, nome):
        app = App.get_running_app()
        if hasattr(app, "sm") and app.sm:
            app.sm.current = nome
        elif self.manager:
            self.manager.current = nome
