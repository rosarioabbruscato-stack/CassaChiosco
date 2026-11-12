# -*- coding: utf-8 -*-
import os, json, csv
try:
    import pandas as pd
except ImportError:
    pd = None

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image as KivyImage
from kivy.graphics import Color, Rectangle
from kivy.app import App

DB_FILE = "magazzino_data.json"

def importa_magazzino_excel(filepath):
    import pandas as pd
    import openpyxl
    articoli_caricati = []
    
    os.makedirs("assets/images", exist_ok=True)
    
    # Tentiamo di estrarre immagini incorporate con openpyxl
    image_map = {}
    try:
        wb = openpyxl.load_workbook(filepath, data_only=True)
        sheet = wb.active
        if hasattr(sheet, "_images") and sheet._images:
            for img in sheet._images:
                row_idx = getattr(img.anchor._from, "row", None)
                if row_idx is not None:
                    # row_idx in openpyxl is 0-indexed (row 1 is index 0, ma l intestazione è row 0 / index 1)
                    # salviamo l immagine su disco
                    img_filename = f"assets/images/img_row_{row_idx}.png"
                    with open(img_filename, "wb") as img_file:
                        img_file.write(img._data())
                    image_map[row_idx + 1] = img_filename # 1-based row index matching pandas df.iterrows() + 2
    except Exception as ex:
        print("Nota estrazione immagini excel:", ex)

    try:
        df = pd.read_excel(filepath)
        for df_idx, row in df.iterrows():
            nome = str(row.get("Nome", "Senza Nome"))
            if pd.isna(nome) or nome.strip() == "": nome = "Senza Nome"
            
            bc = row.get("Codice a barre", "")
            if pd.notna(bc):
                if str(bc).replace(".","").isdigit():
                    barcode = str(int(float(bc)))
                else:
                    barcode = str(bc).strip()
            else:
                barcode = ""
            
            cat = row.get("Magazzino", row.get("Etichette", "Generale"))
            if pd.isna(cat) or str(cat).strip() == "": cat = "Generale"
            else: cat = str(cat).strip()
                
            lotto = row.get("Riferimento interno", "N/D")
            if pd.isna(lotto) or str(lotto).strip() == "": lotto = "N/D"
            else: lotto = str(lotto).strip()
                
            scad = row.get("Data di scadenza", "")
            if pd.notna(scad):
                scad_str = str(scad).strip()
                scad = scad_str[:10] if len(scad_str) >= 10 else ""
            else:
                scad = ""
                
            try:
                prezzo = float(row.get("Prezzo di vendita", 0.0))
            except:
                prezzo = 0.0
                
            try:
                giac = float(row.get("Quantità giacenza fisica", 0.0))
            except:
                giac = 0.0
                
            # Percorso foto: controlliamo se specificato in cella o estratto dal foglio
            foto = row.get("Foto", "")
            foto_str = str(foto).strip() if pd.notna(foto) else ""
            
            # Se non c è nel testo ma c è nell mapping openpyxl delle righe excel (df_idx + 2 corrisponde alla riga excel reale)
            excel_row_num = df_idx + 2
            if not foto_str and excel_row_num in image_map:
                foto_str = image_map[excel_row_num]

            art = {
                "nome": nome,
                "barcode": barcode,
                "cat": cat,
                "lotto": lotto,
                "scad": scad,
                "prezzo": prezzo,
                "giac": giac,
                "pos": "Reparto 1",
                "colore": "#333333",
                "foto": foto_str,
                "selezionato": False
            }
            articoli_caricati.append(art)
    except Exception as e:
        print("Errore importazione excel:", e)
    return articoli_caricati

class FileChooserPopup(Popup):
    def __init__(self, callback, mode="open", **kwargs):
        super(FileChooserPopup, self).__init__(**kwargs)
        self.callback = callback
        self.mode = mode
        self.title = "Seleziona file Excel/CSV da Importare" if mode == "open" else "Scegli dove Esportare il file"
        self.size_hint = (0.85, 0.85)
        layout = BoxLayout(orientation="vertical", spacing=10, padding=10)
        start_path = "/mnt/c/Users/utente/Desktop" if os.path.exists("/mnt/c/Users/utente/Desktop") else os.path.expanduser("~")
        self.fc = FileChooserListView(filters=["*.xlsx", "*.xls", "*.csv"], path=start_path)
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
            self.callback(selection[0])
            self.dismiss()
        elif self.mode == "save" and self.fc.path:
            self.callback(os.path.join(self.fc.path, "magazzino_export.csv"))
            self.dismiss()

class InterfacciaMagazzino(Screen):
    def __init__(self, **kwargs):
        super(InterfacciaMagazzino, self).__init__(**kwargs)
        self.articoli = self.carica_dati()
        self.articolo_selezionato_idx = None
        self.vista_attuale = "elenco"
        self.pagina_corrente = 0
        self.elementi_per_pagina = 40
        
        with self.canvas.before:
            Color(0.92, 0.92, 0.92, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        root = BoxLayout(orientation="vertical", spacing=0, padding=0, size_hint=(1, 1))

        # 1. Tab superiori di navigazione
        top_tabs = BoxLayout(size_hint_y=None, height=45, spacing=2)
        btn_cassa = Button(text="Cassa / Vendita", background_normal="", background_color=(0.25, 0.25, 0.25, 1), bold=True)
        btn_cassa.bind(on_press=lambda x: self.vai_a("cassa"))
        btn_mag = Button(text="Magazzino", background_normal="", background_color=(0.15, 0.1, 0.4, 1), bold=True)
        btn_st = Button(text="Chiusura & Storico", background_normal="", background_color=(0.25, 0.25, 0.25, 1), bold=True)
        btn_st.bind(on_press=lambda x: self.vai_a("chiusura"))
        top_tabs.add_widget(btn_cassa)
        top_tabs.add_widget(btn_mag)
        top_tabs.add_widget(btn_st)
        root.add_widget(top_tabs)

        # 2. Barra superiore azioni
        odoo_bar = BoxLayout(size_hint_y=None, height=50, padding=8, spacing=10)
        odoo_bar.add_widget(Label(text="Gestione Magazzino (Stile Odoo)", color=(0.1,0.1,0.1,1), bold=True, font_size=18, halign="left"))
        
        self.btn_elenco = Button(text="Elenco", size_hint_x=None, width=90, background_normal="", background_color=(0.1, 0.4, 0.6, 1), bold=True)
        self.btn_elenco.bind(on_press=lambda x: self.cambia_vista("elenco"))
        
        self.btn_griglia = Button(text="Vista Griglia", size_hint_x=None, width=100, background_normal="", background_color=(0.2, 0.2, 0.2, 1), bold=True)
        self.btn_griglia.bind(on_press=lambda x: self.cambia_vista("griglia"))
        
        btn_esp = Button(text="Esporta Excel", size_hint_x=None, width=110, background_normal="", background_color=(0.1, 0.6, 0.3, 1), bold=True)
        btn_esp.bind(on_press=lambda x: self.apri_selettore_salvataggio())
        btn_imp = Button(text="Importa Excel", size_hint_x=None, width=110, background_normal="", background_color=(0.15, 0.4, 0.7, 1), bold=True)
        btn_imp.bind(on_press=lambda x: self.apri_selettore_apertura())
        btn_allerta = Button(text="⚠ Allerta", size_hint_x=None, width=90, background_normal="", background_color=(0.6, 0.1, 0.1, 1), bold=True)
        btn_allerta.bind(on_press=self.filtra_scorte_basse)
        
        odoo_bar.add_widget(self.btn_elenco)
        odoo_bar.add_widget(self.btn_griglia)
        odoo_bar.add_widget(btn_esp)
        odoo_bar.add_widget(btn_imp)
        odoo_bar.add_widget(btn_allerta)
        root.add_widget(odoo_bar)

        # 3. Barra filtri e selezione totale
        filter_bar = BoxLayout(size_hint_y=None, height=45, padding=5, spacing=8)
        self.txt_cerca = TextInput(hint_text="Cerca per nome o codice...", multiline=False, size_hint_x=0.45)
        self.txt_cerca.bind(text=self.cerca_articoli)
        btn_raggruppa = Button(text="Raggruppa per...", size_hint_x=0.2, background_normal="", background_color=(0.3, 0.3, 0.3, 1))
        btn_sel = Button(text="Sel. Tutti", size_hint_x=0.175, background_normal="", background_color=(0.2, 0.5, 0.2, 1), bold=True)
        btn_sel.bind(on_press=self.seleziona_tutti)
        btn_des = Button(text="Deselez.", size_hint_x=0.175, background_normal="", background_color=(0.5, 0.2, 0.2, 1), bold=True)
        btn_des.bind(on_press=self.deseleziona_tutti)
        
        filter_bar.add_widget(self.txt_cerca)
        filter_bar.add_widget(btn_raggruppa)
        filter_bar.add_widget(btn_sel)
        filter_bar.add_widget(btn_des)
        root.add_widget(filter_bar)

        # 4. Area Principale
        main_split = BoxLayout(orientation="horizontal", padding=8, spacing=12, size_hint=(1, 1))

        # Colonna Sinistra
        left_layout = BoxLayout(orientation="vertical", spacing=5, size_hint_x=0.5)
        
        header_list_row = BoxLayout(size_hint_y=None, height=30, spacing=5)
        self.btn_master_chk = Button(text="[   ]", size_hint_x=None, width=45, background_normal="", background_color=(0.85, 0.85, 0.85, 1), color=(0,0,0,1), bold=True)
        self.btn_master_chk.bind(on_press=self.toggle_master_seleziona)
        self.lbl_stato_lista = Label(text="Elenco Articoli Dettagliato (Paginato)", color=(0.1,0.1,0.1,1), bold=True, halign="left")
        self.lbl_stato_lista.bind(size=self.lbl_stato_lista.setter("text_size"))
        header_list_row.add_widget(self.btn_master_chk)
        header_list_row.add_widget(self.lbl_stato_lista)
        left_layout.add_widget(header_list_row)
        
        self.scroll_list = ScrollView(size_hint_y=1)
        self.list_content = BoxLayout(orientation="vertical", spacing=4, size_hint_y=None)
        self.list_content.bind(minimum_height=self.list_content.setter("height"))
        self.scroll_list.add_widget(self.list_content)
        left_layout.add_widget(self.scroll_list)

        # Paginazione in basso a sinistra
        page_bar = BoxLayout(size_hint_y=None, height=40, spacing=10)
        btn_prev = Button(text="« Precedente", background_normal="", background_color=(0.3, 0.3, 0.3, 1), bold=True)
        btn_prev.bind(on_press=self.pagina_precedente)
        self.lbl_pagina = Label(text="Pagina 1", color=(0.1,0.1,0.1,1), bold=True)
        btn_next = Button(text="Successivo »", background_normal="", background_color=(0.3, 0.3, 0.3, 1), bold=True)
        btn_next.bind(on_press=self.pagina_successiva)
        
        page_bar.add_widget(btn_prev)
        page_bar.add_widget(self.lbl_pagina)
        page_bar.add_widget(btn_next)
        left_layout.add_widget(page_bar)

        main_split.add_widget(left_layout)

        # Colonna Destra (Form Modifica)
        right_layout = BoxLayout(orientation="vertical", spacing=8, size_hint_x=0.5, padding=5)
        
        row_nome_foto = BoxLayout(size_hint_y=None, height=75, spacing=10)
        box_campi_nome = BoxLayout(orientation="vertical", spacing=3)
        box_campi_nome.add_widget(Label(text="Nome Prodotto:", color=(0.1,0.1,0.1,1), font_size=12, halign="left", size_hint_y=None, height=20))
        self.txt_nome = TextInput(hint_text="Nome prodotto", multiline=False)
        box_campi_nome.add_widget(self.txt_nome)
        row_nome_foto.add_widget(box_campi_nome)
        
        box_foto = BoxLayout(orientation="vertical", size_hint_x=None, width=120)
        box_foto.add_widget(Label(text="Foto Prodotto", color=(0.1,0.1,0.1,1), font_size=11, size_hint_y=None, height=18))
        self.btn_foto_form = Button(text="[□ Quadrata\n130 x 130]", background_normal="", background_color=(0.85, 0.85, 0.85, 1), color=(0.4,0.4,0.4,1), font_size=11)
        box_foto.add_widget(self.btn_foto_form)
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
        
        self.clear_widgets()
        self.add_widget(root)
        self.aggiorna_lista_video()

    def crea_campo(self, parent, label_text, hint):
        row_f = BoxLayout(size_hint_y=None, height=35, spacing=10)
        lbl = Label(text=label_text, color=(0.1,0.1,0.1,1), font_size=12, size_hint_x=0.45, halign="right")
        lbl.bind(size=lbl.setter("text_size"))
        ti = TextInput(text="0.00" if hint=="0.00" else ("0.0" if hint=="0.0" else ("#333333" if hint=="#333333" else "")), hint_text=hint, multiline=False, size_hint_x=0.55)
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
            {"nome": "Prodotto Test 1", "barcode": "123456", "cat": "Bevande", "lotto": "A1", "scad": "2027-01-01", "prezzo": 5.00, "giac": 10.0, "pos": "Reparto 1", "colore": "#ff5500", "foto": "", "selezionato": False},
            {"nome": "Prodotto Test 2", "barcode": "654321", "cat": "Snack", "lotto": "B2", "scad": "2027-06-01", "prezzo": 3.50, "giac": 25.0, "pos": "Reparto 2", "colore": "#ffdd00", "foto": "", "selezionato": False}
        ]

    def salva_dati(self):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(self.articoli, f, indent=4, ensure_ascii=False)

    def cambia_vista(self, tipo):
        self.vista_attuale = tipo
        if tipo == "elenco":
            self.btn_elenco.background_color = (0.1, 0.4, 0.6, 1)
            self.btn_griglia.background_color = (0.2, 0.2, 0.2, 1)
        else:
            self.btn_griglia.background_color = (0.1, 0.4, 0.6, 1)
            self.btn_elenco.background_color = (0.2, 0.2, 0.2, 1)
        self.aggiorna_lista_video(self.txt_cerca.text)

    def pagina_precedente(self, *args):
        if self.pagina_corrente > 0:
            self.pagina_corrente -= 1
            self.aggiorna_lista_video(self.txt_cerca.text)

    def pagina_successiva(self, *args):
        filtro = self.txt_cerca.text.lower()
        filtrati = [a for a in self.articoli if not filtro or filtro in a["nome"].lower() or filtro in a["barcode"].lower()]
        tot_pagine = max(1, (len(filtrati) + self.elementi_per_pagina - 1) // self.elementi_per_pagina)
        if self.pagina_corrente < tot_pagine - 1:
            self.pagina_corrente += 1
            self.aggiorna_lista_video(self.txt_cerca.text)

    def apri_selettore_apertura(self):
        FileChooserPopup(callback=self.importa_file, mode="open").open()

    def apri_selettore_salvataggio(self):
        FileChooserPopup(callback=self.esporta_file, mode="save").open()

    def esporta_file(self, filepath):
        try:
            if filepath.endswith((".xlsx", ".xls")) and pd is not None:
                pd.DataFrame(self.articoli).to_excel(filepath, index=False)
            else:
                with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
                    w = csv.writer(f, delimiter=";")
                    w.writerow(["Nome", "Barcode", "Categoria", "Lotto", "Scadenza", "Prezzo", "Giacenza", "POS", "Colore", "Foto"])
                    for a in self.articoli:
                        w.writerow([a.get("nome", ""), a.get("barcode", ""), a.get("cat", ""), a.get("lotto", ""), a.get("scad", ""), a.get("prezzo", 0), a.get("giac", 0), a.get("pos", ""), a.get("colore", ""), a.get("foto", "")])
            self.lbl_stato_lista.text = "Esportato con successo!"
        except Exception as e:
            self.lbl_stato_lista.text = "Errore: " + str(e)

    def importa_file(self, filepath):
        if not os.path.exists(filepath): return
        try:
            nuovi = importa_magazzino_excel(filepath)
            if nuovi:
                self.articoli = nuovi
                self.salva_dati()
                self.pagina_corrente = 0
                self.aggiorna_lista_video()
                self.lbl_stato_lista.text = "Importati " + str(len(nuovi)) + " articoli!"
        except Exception as e:
            self.lbl_stato_lista.text = "Errore import: " + str(e)

    def aggiorna_lista_video(self, filtro=""):
        self.list_content.clear_widgets()
        
        filtrati = []
        for idx, art in enumerate(self.articoli):
            if filtro and filtro.lower() not in art["nome"].lower() and filtro.lower() not in art["barcode"].lower():
                continue
            filtrati.append((idx, art))
            
        tot_elementi = len(filtrati)
        tot_pagine = max(1, (tot_elementi + self.elementi_per_pagina - 1) // self.elementi_per_pagina)
        if self.pagina_corrente >= tot_pagine:
            self.pagina_corrente = max(0, tot_pagine - 1)
            
        self.lbl_pagina.text = f"Pag. {self.pagina_corrente + 1} / {tot_pagine} ({tot_elementi} tot)"
        
        inizio = self.pagina_corrente * self.elementi_per_pagina
        fine = inizio + self.elementi_per_pagina
        pagina_articoli = filtrati[inizio:fine]
        
        if self.vista_attuale == "elenco":
            for real_idx, art in pagina_articoli:
                row = BoxLayout(size_hint_y=None, height=38, spacing=4)
                chk_btn = Button(text="[ X ]" if art.get("selezionato") else "[   ]", size_hint_x=None, width=40, background_normal="", background_color=(0.85, 0.85, 0.85, 1), color=(0,0,0,1), bold=True)
                chk_btn.bind(on_press=lambda inst, i=real_idx: self.toggle_seleziona(i))
                
                txt = f"📦 {art['nome']} | EAN: {art.get('barcode','-')} | Cat: {art['cat']} | Lotto: {art['lotto']} | Scad: {art.get('scad','-')} | CHF {art['prezzo']} | Giac: {art['giac']}"
                btn = Button(text=txt, background_normal="", background_color=(0.95, 0.95, 0.95, 1), color=(0.1,0.1,0.1,1), font_size=12, halign="left")
                btn.bind(size=btn.setter("text_size"))
                btn.bind(on_press=lambda inst, i=real_idx: self.carica_articolo_in_form(i))
                
                row.add_widget(chk_btn)
                row.add_widget(btn)
                self.list_content.add_widget(row)
        else:
            grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
            grid.bind(minimum_height=grid.setter("height"))
            for real_idx, art in pagina_articoli:
                card = BoxLayout(orientation="vertical", size_hint_y=None, height=130, padding=6, spacing=4)
                with card.canvas.before:
                    Color(0.88, 0.88, 0.88, 1)
                    Rectangle(size=card.size, pos=card.pos)
                card.bind(size=lambda c, s: setattr(c.canvas.before.children[-1], 'size', s))
                
                top_card = BoxLayout(orientation="horizontal", spacing=6, size_hint_y=None, height=70)
                
                foto_path = art.get("foto", "")
                if foto_path and os.path.exists(foto_path):
                    img = KivyImage(source=foto_path, size_hint_x=None, width=70)
                else:
                    img = Button(text="[Foto]", size_hint_x=None, width=70, background_normal="", background_color=(0.8, 0.8, 0.8, 1), color=(0.2,0.2,0.2,1), font_size=11)
                top_card.add_widget(img)
                
                info_box = BoxLayout(orientation="vertical", spacing=2)
                lbl_n = Label(text=art['nome'], color=(0.1,0.1,0.1,1), bold=True, font_size=12, halign="left")
                lbl_n.bind(size=lbl_n.setter("text_size"))
                lbl_d = Label(text=f"CHF {art['prezzo']} | Giac: {art['giac']}\nCat: {art['cat']}", color=(0.3,0.3,0.3,1), font_size=11, halign="left")
                lbl_d.bind(size=lbl_d.setter("text_size"))
                info_box.add_widget(lbl_n)
                info_box.add_widget(lbl_d)
                top_card.add_widget(info_box)
                
                card.add_widget(top_card)
                
                btn_card = Button(text="Seleziona / Modifica", size_hint_y=None, height=30, background_normal="", background_color=(0.1, 0.4, 0.6, 1), bold=True)
                btn_card.bind(on_press=lambda inst, i=real_idx: self.carica_articolo_in_form(i))
                card.add_widget(btn_card)
                
                grid.add_widget(card)
            self.list_content.add_widget(grid)
        
        if self.articoli and all(a.get("selezionato", False) for a in self.articoli):
            self.btn_master_chk.text = "[ X ]"
        else:
            self.btn_master_chk.text = "[   ]"

    def toggle_master_seleziona(self, *args):
        tutti_selezionati = all(a.get("selezionato", False) for a in self.articoli) if self.articoli else False
        status = not tutti_selezionati
        for a in self.articoli:
            a["selezionato"] = status
        self.btn_master_chk.text = "[ X ]" if status else "[   ]"
        self.aggiorna_lista_video(self.txt_cerca.text)

    def toggle_seleziona(self, idx):
        self.articoli[idx]["selezionato"] = not self.articoli[idx].get("selezionato", False)
        self.aggiorna_lista_video(self.txt_cerca.text)

    def seleziona_tutti(self, *args):
        for a in self.articoli: a["selezionato"] = True
        self.btn_master_chk.text = "[ X ]"
        self.aggiorna_lista_video(self.txt_cerca.text)

    def deseleziona_tutti(self, *args):
        for a in self.articoli: a["selezionato"] = False
        self.btn_master_chk.text = "[   ]"
        self.aggiorna_lista_video(self.txt_cerca.text)

    def cerca_articoli(self, inst, val):
        self.pagina_corrente = 0
        self.aggiorna_lista_video(val)

    def filtra_scorte_basse(self, *args):
        self.list_content.clear_widgets()
        for idx, art in enumerate(self.articoli):
            if art["giac"] <= 2.0:
                row = BoxLayout(size_hint_y=None, height=35, spacing=5)
                chk_btn = Button(text="[ X ]" if art.get("selezionato") else "[   ]", size_hint_x=None, width=45, background_normal="", background_color=(0.85, 0.85, 0.85, 1), color=(0,0,0,1), bold=True)
                chk_btn.bind(on_press=lambda inst, i=idx: self.toggle_seleziona(i))
                btn = Button(text="[ALLERTA] " + art["nome"] + " | Giac: " + str(art["giac"]), background_normal="", background_color=(1, 0.8, 0.8, 1), color=(0.8,0,0,1), halign="left")
                btn.bind(size=btn.setter("text_size"))
                btn.bind(on_press=lambda inst, i=idx: self.carica_articolo_in_form(i))
                row.add_widget(chk_btn)
                row.add_widget(btn)
                self.list_content.add_widget(row)
        self.lbl_stato_lista.text = "Elenco Articoli (Filtro Scorte Basse)"

    def carica_articolo_in_form(self, idx):
        self.articolo_selezionato_idx = idx
        a = self.articoli[idx]
        self.txt_nome.text = str(a.get("nome", ""))
        self.txt_barcode.text = str(a.get("barcode", ""))
        self.txt_cat.text = str(a.get("cat", "Generale"))
        self.txt_lotto.text = str(a.get("lotto", "N/D"))
        self.txt_scad.text = str(a.get("scad", ""))
        self.txt_prezzo.text = str(a.get("prezzo", 0.0))
        self.txt_giac.text = str(a.get("giac", 0.0))
        self.txt_pos.text = str(a.get("pos", "Reparto 1"))
        self.txt_colore.text = str(a.get("colore", "#333333"))
        self.lbl_stato_lista.text = "In modifica: " + a.get("nome", "") + " (ID: " + str(idx) + ")"

    def salva_articolo(self, *args):
        try:
            p = float(self.txt_prezzo.text.replace(",", ".") or 0)
            g = float(self.txt_giac.text.replace(",", ".") or 0)
        except:
            p, g = 0.0, 0.0
        art = {
            "nome": self.txt_nome.text.strip() or "Senza Nome",
            "barcode": self.txt_barcode.text.strip(),
            "cat": self.txt_cat.text.strip() or "N/D",
            "lotto": self.txt_lotto.text.strip() or "N/D",
            "scad": self.txt_scad.text.strip(),
            "prezzo": p,
            "giac": g,
            "pos": self.txt_pos.text.strip(),
            "colore": self.txt_colore.text.strip() or "#333333",
            "foto": self.articoli[self.articolo_selezionato_idx].get("foto", "") if self.articolo_selezionato_idx is not None and self.articolo_selezionato_idx < len(self.articoli) else "",
            "selezionato": False
        }
        if self.articolo_selezionato_idx is not None and self.articolo_selezionato_idx < len(self.articoli):
            self.articoli[self.articolo_selezionato_idx] = art
        else:
            self.articoli.append(art)
        self.salva_dati()
        self.aggiorna_lista_video(self.txt_cerca.text)
        self.pulisci_form()
        self.lbl_stato_lista.text = "Articolo salvato e aggiornato correttamente!"

    def elimina_articolo(self, *args):
        nuovi = [a for a in self.articoli if not a.get("selezionato", False)]
        if len(nuovi) == len(self.articoli) and self.articolo_selezionato_idx is not None:
            if self.articolo_selezionato_idx < len(self.articoli):
                del self.articoli[self.articolo_selezionato_idx]
        else:
            self.articoli = nuovi
        self.articolo_selezionato_idx = None
        self.salva_dati()
        self.aggiorna_lista_video(self.txt_cerca.text)
        self.pulisci_form()
        self.lbl_stato_lista.text = "Articolo/i eliminato/i con successo!"

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
        self.bg_rect.pos = (0, 0)
        self.bg_rect.size = (self.width, self.height)

    def vai_a(self, nome):
        app = App.get_running_app()
        if hasattr(app, "sm") and app.sm:
            app.sm.current = nome
        elif self.manager:
            self.manager.current = nome
