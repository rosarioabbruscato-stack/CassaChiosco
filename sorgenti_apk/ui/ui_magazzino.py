import os
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
import sqlite3
from database.db_manager import DB_PATH
from logic.excel_manager import esporta_magazzino_excel, importa_magazzino_excel

class InterfacciaMagazzino(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(10)
        self.spacing = dp(10)
        self.prodotto_selezionato_id = None
        self.checkboxes_prodotti = {}
        self.modalita_vista = 'elenco'
        self.criteri_raggruppamento_attivi = []

        top_layout = BoxLayout(size_hint_y=None, height=45, spacing=10)
        top_layout.add_widget(Label(text="Gestione Magazzino (Stile Odoo)", font_size=18, bold=True, color=(0.1, 0.1, 0.1, 1)))
        
        self.btn_vista_elenco = Button(text='Elenco', size_hint_x=None, width=95, background_color=(0.1, 0.4, 0.6, 1))
        self.btn_vista_griglia = Button(text='Griglia', size_hint_x=None, width=95, background_color=(0.1, 0.4, 0.6, 1))
        self.btn_esporta_excel = Button(text='Esporta', size_hint_x=None, width=95, background_color=(0.2, 0.6, 0.2, 1))
        self.btn_vista_elenco.bind(on_press=lambda x: self.cambia_vista('elenco'))
        top_layout.add_widget(self.btn_vista_elenco)

        self.btn_vista_griglia = Button(text="Vista Griglia", size_hint_x=None, width=110, background_color=(0.3, 0.3, 0.3, 1))
        self.btn_vista_griglia.bind(on_press=lambda x: self.cambia_vista('griglia'))
        top_layout.add_widget(self.btn_vista_griglia)

        btn_export = Button(text="Esporta Excel", size_hint_x=None, width=110, background_color=(0.1, 0.6, 0.2, 1))
        btn_export.bind(on_press=self.esporta_dati)
        top_layout.add_widget(btn_export)

        btn_import = Button(text="Importa Excel", size_hint_x=None, width=110, background_color=(0.2, 0.4, 0.8, 1))
        btn_import.bind(on_press=self.importa_dati)
        top_layout.add_widget(btn_import)
        
        self.add_widget(top_layout)

        filter_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        self.input_ricerca = TextInput(text='', hint_text='Cerca per nome o codice...', multiline=False, size_hint_x=0.35)
        self.input_ricerca.bind(text=lambda instance, value: self.aggiorna_lista_prodotti())
        filter_layout.add_widget(self.input_ricerca)

        self.btn_filtro_avanzato = Button(text='Raggruppa per...', size_hint_x=0.35, background_color=(0.2, 0.2, 0.2, 1))
        self.btn_filtro_avanzato.bind(on_release=self.apri_popup_raggruppamento)
        filter_layout.add_widget(self.btn_filtro_avanzato)

        btn_sel_all = Button(text='Sel. Tutti', size_hint_x=0.15)
        btn_sel_all.bind(on_press=self.seleziona_tutti)
        filter_layout.add_widget(btn_sel_all)

        btn_desel_all = Button(text='Deselez.', size_hint_x=0.15)
        btn_desel_all.bind(on_press=self.deseleziona_tutti)
        filter_layout.add_widget(btn_desel_all)

        self.add_widget(filter_layout)

        body_layout = BoxLayout(orientation='horizontal', spacing=15)

        left_layout = BoxLayout(orientation='vertical', size_hint_x=0.5, spacing=5)
        
        header_lista_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=30, spacing=5)
        self.chk_master = CheckBox(size_hint_x=None, width=35, color=(0.1, 0.4, 0.8, 1))
        self.chk_master.bind(active=self.toggle_seleziona_tutti_master)
        header_lista_box.add_widget(self.chk_master)

        self.label_titolo_lista = Label(text='Elenco Articoli (Tutti / Seleziona)', font_size=14, bold=True, color=(0.1, 0.1, 0.1, 1), halign='left')
        self.label_titolo_lista.bind(size=lambda s, w: setattr(s, 'text_size', (s.width, s.height)))
        header_lista_box.add_widget(self.label_titolo_lista)
        
        left_layout.add_widget(header_lista_box)
        
        self.scroll_lista = ScrollView()
        self.layout_lista_prodotti = GridLayout(cols=1, spacing=2, size_hint_y=None)
        self.layout_lista_prodotti.bind(minimum_height=self.layout_lista_prodotti.setter('height'))
        self.scroll_lista.add_widget(self.layout_lista_prodotti)
        left_layout.add_widget(self.scroll_lista)
        
        body_layout.add_widget(left_layout)

        right_main_layout = BoxLayout(orientation='vertical', size_hint_x=0.5, spacing=8, padding=10)

        header_odoo = BoxLayout(size_hint_y=None, height=135, spacing=10)
        
        fields_left_header = BoxLayout(orientation='vertical', spacing=6)
        
        name_box = BoxLayout(orientation='vertical', spacing=2)
        name_box.add_widget(Label(text='Nome Prodotto:', font_size=12, size_hint_y=None, height=18, color=(0.1, 0.1, 0.1, 1), halign='left'))
        self.input_nome = TextInput(text='', multiline=False, font_size=14)
        name_box.add_widget(self.input_nome)
        fields_left_header.add_widget(name_box)

        barcode_box = BoxLayout(orientation='vertical', spacing=2)
        barcode_box.add_widget(Label(text='Codice a barre (EAN):', font_size=12, size_hint_y=None, height=18, color=(0.1, 0.1, 0.1, 1), halign='left'))
        self.input_barcode = TextInput(text='', multiline=False, font_size=13)
        barcode_box.add_widget(self.input_barcode)
        fields_left_header.add_widget(barcode_box)

        header_odoo.add_widget(fields_left_header)

        foto_box = BoxLayout(orientation='vertical', size_hint_x=None, width=130, spacing=2)
        foto_box.add_widget(Label(text='Foto Prodotto', font_size=12, bold=True, size_hint_y=None, height=18, color=(0.1, 0.1, 0.1, 1)))
        
        # Pulsante Scegli Immagine
        # btn_rimosso = Button(text='Scegli Immagine...', size_hint_y=None, height=35, background_color=(0.1, 0.4, 0.7, 1))
        # btn_rimosso.bind(on_press=self.seleziona_immagine)
        # rimosso nome errato

        self.input_foto = TextInput(text='', multiline=False, font_size=11, hint_text='Path immagine...', size_hint_y=None, height=30)
        self.btn_anteprima_foto = Button(text='[ 📷 Quadrata\n130 x 130 ]', font_size=12, background_color=(0.88, 0.88, 0.90, 1), color=(0.2, 0.2, 0.2, 1))
        self.btn_anteprima_foto.bind(on_press=self.seleziona_immagine)
        
        foto_box.add_widget(self.btn_anteprima_foto)
        foto_box.add_widget(self.input_foto)
        header_odoo.add_widget(foto_box)

        right_main_layout.add_widget(header_odoo)

        form_grid = GridLayout(cols=2, spacing=8, padding=5)
        
        form_grid.add_widget(Label(text='Categoria:', color=(0.1, 0.1, 0.1, 1)))
        self.spinner_categoria = Spinner(text='Seleziona o scrivi...', values=self.get_valori_colonna('categoria'))
        form_grid.add_widget(self.spinner_categoria)

        form_grid.add_widget(Label(text='Lotto:', color=(0.1, 0.1, 0.1, 1)))
        self.spinner_lotto = Spinner(text='Seleziona o scrivi...', values=self.get_valori_colonna('lotto'))
        form_grid.add_widget(self.spinner_lotto)

        form_grid.add_widget(Label(text='Scadenza (YYYY-MM-DD):', color=(0.1, 0.1, 0.1, 1)))
        self.input_scadenza = TextInput(text='', multiline=False)
        form_grid.add_widget(self.input_scadenza)

        form_grid.add_widget(Label(text='Prezzo di Vendita (CHF):', color=(0.1, 0.1, 0.1, 1)))
        self.input_prezzo = TextInput(text='0.0', multiline=False)
        form_grid.add_widget(self.input_prezzo)

        form_grid.add_widget(Label(text='Giacenza Fisica:', color=(0.1, 0.1, 0.1, 1)))
        self.input_giacenza = TextInput(text='0.0', multiline=False)
        form_grid.add_widget(self.input_giacenza)

        form_grid.add_widget(Label(text='Categoria POS (Doc. Z):', color=(0.1, 0.1, 0.1, 1)))
        self.spinner_categoria_pos = Spinner(text='Seleziona...', values=self.get_valori_colonna('categoria_pos'))
        form_grid.add_widget(self.spinner_categoria_pos)

        form_grid.add_widget(Label(text='Colore Pulsante (Hex):', color=(0.1, 0.1, 0.1, 1)))
        self.input_colore = TextInput(text='#333333', multiline=False)
        form_grid.add_widget(self.input_colore)

        right_main_layout.add_widget(form_grid)

        actions_layout = BoxLayout(size_hint_y=None, height=45, spacing=10)
        btn_salva = Button(text='Salva Modifiche / Nuovo', background_color=(0.1, 0.5, 0.8, 1))
        btn_salva.bind(on_press=self.salva_prodotto)
        actions_layout.add_widget(btn_salva)

        btn_elimina = Button(text='Elimina Selezionati / Corrente', background_color=(0.8, 0.2, 0.2, 1))
        btn_elimina.bind(on_press=self.elimina_prodotto)
        actions_layout.add_widget(btn_elimina)

        right_main_layout.add_widget(actions_layout)

        body_layout.add_widget(right_main_layout)
        self.add_widget(body_layout)

        self.aggiorna_spinner_filtro()
        self.aggiorna_lista_prodotti()

    def cambia_vista(self, vista):
        self.modalita_vista = vista
        if vista == 'elenco':
            self.btn_vista_elenco.background_color = (0.1, 0.4, 0.6, 1)
            self.btn_vista_griglia.background_color = (0.3, 0.3, 0.3, 1)
            self.label_titolo_lista.text = 'Elenco Articoli (Tutti / Seleziona)'
            self.layout_lista_prodotti.cols = 1
        else:
            self.btn_vista_griglia.background_color = (0.1, 0.4, 0.6, 1)
            self.btn_vista_elenco.background_color = (0.3, 0.3, 0.3, 1)
            self.label_titolo_lista.text = 'Vista Griglia / Cartellini (Kanban)'
            self.layout_lista_prodotti.cols = 2
        self.aggiorna_lista_prodotti()

    def get_valori_colonna(self, colonna):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(f"SELECT DISTINCT {colonna} FROM prodotti WHERE {colonna} IS NOT NULL AND {colonna} != '' ORDER BY {colonna} ASC")
            valori = [str(r[0]) for r in cursor.fetchall()]
            conn.close()
            return valori if valori else ['Nessun valore']
        except:
            return ['Nessun valore']

    def apri_popup_raggruppamento(self, instance):
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        criteri = [
            ("Raggruppa per Categoria", "categoria"),
            ("Raggruppa per Lotto", "lotto"),
            ("Raggruppa per Scadenza", "data_scadenza"),
            ("Raggruppa per Prezzo", "prezzo"),
            ("Raggruppa per Giacenza", "giacenza"),
            ("Raggruppa per Categoria POS", "categoria_pos"),
            ("Raggruppa per Colore", "colore_pulsante")
        ]

        scroll = ScrollView(size_hint=(1, 1))
        grid = GridLayout(cols=1, spacing=8, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        checkboxes_popup = {}

        for titolo, chiave in criteri:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
            chk = CheckBox(size_hint_x=None, width=40, color=(0.1, 0.4, 0.8, 1))
            if chiave in self.criteri_raggruppamento_attivi:
                chk.active = True
            checkboxes_popup[chiave] = chk
            row.add_widget(chk)

            lbl_item = Label(text=titolo, font_size=15, bold=True, halign='left', valign='middle', color=(1, 1, 1, 1))
            lbl_item.bind(size=lambda s, w: setattr(s, 'text_size', (s.width - 10, s.height)))
            row.add_widget(lbl_item)
            grid.add_widget(row)

        scroll.add_widget(grid)
        content.add_widget(scroll)

        bottom_btns = BoxLayout(size_hint_y=None, height=45, spacing=10)
        btn_applica = Button(text='Applica Raggruppamento', background_color=(0.1, 0.4, 0.7, 1))
        btn_annulla = Button(text='Chiudi', background_color=(0.5, 0.5, 0.5, 1))
        bottom_btns.add_widget(btn_applica)
        bottom_btns.add_widget(btn_annulla)
        content.add_widget(bottom_btns)

        popup = Popup(title='Raggruppa per (Stile Odoo)', content=content, size_hint=(0.65, 0.75))

        def applica_e_chiudi(instance):
            try:
                self.criteri_raggruppamento_attivi = [chiave for chiave, chk in checkboxes_popup.items() if chk.active]
                if self.criteri_raggruppamento_attivi:
                    self.btn_filtro_avanzato.text = f"Raggruppato per ({len(self.criteri_raggruppamento_attivi)} livelli)"
                else:
                    self.btn_filtro_avanzato.text = "Raggruppa per..."
                self.aggiorna_lista_prodotti()
            except Exception as e:
                print("Errore ordinamento:", e)
            finally:
                popup.dismiss()

    def aggiorna_spinner_filtro(self):
        cat_vals = self.get_valori_colonna('categoria')
        self.spinner_categoria.values = cat_vals if cat_vals else ['Seleziona o scrivi...']
        
        lotto_vals = self.get_valori_colonna('lotto')
        self.spinner_lotto.values = lotto_vals if lotto_vals else ['Seleziona o scrivi...']
        
        pos_vals = self.get_valori_colonna('categoria_pos')
        self.spinner_categoria_pos.values = pos_vals if pos_vals else ['Seleziona...']

    def toggle_seleziona_tutti_master(self, instance, value):
        for chk in self.checkboxes_prodotti.values():
            chk.active = value

    def aggiorna_lista_prodotti(self):
        self.layout_lista_prodotti.clear_widgets()
        self.checkboxes_prodotti.clear()

        testo_ricerca = self.input_ricerca.text.strip().lower()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Migrazione automatica delle colonne mancanti
        cursor.execute("PRAGMA table_info(prodotti)")
        colonne_esistenti = [col[1] for col in cursor.fetchall()]
        colonne_richieste = {
            "codice_barra": "TEXT",
            "categoria": "TEXT",
            "lotto": "TEXT",
            "data_scadenza": "TEXT",
            "categoria_pos": "TEXT",
            "colore_pulsante": "TEXT"
        }
        for col_nome, col_tipo in colonne_richieste.items():
            if col_nome not in colonne_esistenti:
                cursor.execute(f"ALTER TABLE prodotti ADD COLUMN {col_nome} {col_tipo}")
                conn.commit()

        cursor.execute("SELECT id, codice_barra, nome, prezzo, categoria, giacenza, lotto, data_scadenza, categoria_pos, colore_pulsante FROM prodotti ORDER BY nome ASC")
        prodotti = cursor.fetchall()
        conn.close()

        mappa_indici = {
            'categoria': 4,
            'lotto': 6,
            'data_scadenza': 7,
            'prezzo': 3,
            'giacenza': 5,
            'categoria_pos': 8,
            'colore_pulsante': 9
        }

        if self.criteri_raggruppamento_attivi:
            def chiave_ordinamento(prod):
                chiavi_tupla = []
                for c in self.criteri_raggruppamento_attivi:
                    idx = mappa_indici[c]
                    val = prod[idx]
                    if c in ['prezzo', 'giacenza']:
                        try:
                            chiavi_tupla.append(float(val or 0.0))
                        except:
                            chiavi_tupla.append(0.0)
                    else:
                        chiavi_tupla.append(str(val or 'Senza Valore'))
                return tuple(chiavi_tupla)

            try:
                prodotti.sort(key=chiave_ordinamento)
            except Exception as e:
                print("Errore ordinamento:", e)

        ultimi_valori_gruppo = {}

        for p in prodotti:
            p_id, barcode, nome, prezzo, categoria, giacenza, lotto, scadenza, cat_pos, colore = p
            nome_str = str(nome or 'Senza Nome')
            barcode_str = str(barcode or 'N/D')
            cat_str = str(categoria or 'N/D')
            lotto_str = str(lotto or 'N/D')
            scad_str = str(scadenza or 'N/D')
            prezzo_val = float(prezzo or 0.0)
            giac_val = float(giacenza or 0.0)
            pos_str = str(cat_pos or 'N/D')
            col_str = str(colore or 'N/D')

            mappa_valori_correnti = {
                'categoria': cat_str,
                'lotto': lotto_str,
                'data_scadenza': scad_str,
                'prezzo': f"CHF {prezzo_val:.2f}",
                'giacenza': f"{giac_val}",
                'categoria_pos': pos_str,
                'colore_pulsante': col_str
            }

            if self.criteri_raggruppamento_attivi:
                for idx_livello, criterio in enumerate(self.criteri_raggruppamento_attivi):
                    val_curr = mappa_valori_correnti[criterio]
                    livello_chiave = tuple(self.criteri_raggruppamento_attivi[:idx_livello+1])
                    
                    if ultimi_valori_gruppo.get(livello_chiave) != val_curr:
                        ultimi_valori_gruppo[livello_chiave] = val_curr
                        for k in list(ultimi_valori_gruppo.keys()):
                            if len(k) > len(livello_chiave):
                                del ultimi_valori_gruppo[k]

                        indentazione = "    " * idx_livello
                        lbl_gruppo = Label(
                            text=f"{indent}📂 {criterio.upper()}: {val_curr}", 
                            font_size=13 - idx_livello, 
                            bold=True, 
                            size_hint_y=None, 
                            height=28, 
                            color=(0.1 + (idx_livello*0.1), 0.4, 0.8 - (idx_livello*0.1), 1),
                            halign='left'
                        )
                        lbl_gruppo.bind(size=lambda s, w: setattr(s, 'text_size', (s.width - 10, s.height)))
                        self.layout_lista_prodotti.add_widget(lbl_gruppo)

            if testo_ricerca and (testo_ricerca not in nome_str.lower() and testo_ricerca not in barcode_str.lower()):
                continue

            if self.modalita_vista == 'elenco':
                row_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=32, spacing=5)
                
                chk = CheckBox(size_hint_x=None, width=35, color=(0.1, 0.4, 0.8, 1))
                if self.chk_master.active:
                    chk.active = True
                self.checkboxes_prodotti[p_id] = chk
                row_box.add_widget(chk)

                testo_riga = f"{nome_str}    |    Cat: {cat_str}    |    Lotto: {lotto_str}    |    CHF {prezzo_val:.2f}    |    Giac: {giac_val}"
                
                btn_riga = Button(text=testo_riga, font_size=13, background_normal='', background_color=(0, 0, 0, 0), color=(0, 0, 0, 1), halign='left', valign='middle')
                btn_riga.bind(size=lambda s, w: setattr(s, 'text_size', (s.width - 10, s.height)))
                btn_riga.bind(on_press=lambda instance, pid=p_id: self.seleziona_prodotto(pid))
                row_box.add_widget(btn_riga)

                self.layout_lista_prodotti.add_widget(row_box)
            else:
                card_box = BoxLayout(orientation='vertical', size_hint_y=None, height=90, padding=2, spacing=2)
                top_card = BoxLayout(size_hint_y=None, height=25, spacing=5)
                chk = CheckBox(size_hint_x=None, width=25, color=(0.1, 0.4, 0.8, 1))
                if self.chk_master.active:
                    chk.active = True
                self.checkboxes_prodotti[p_id] = chk
                top_card.add_widget(chk)
                
                btn_nome = Button(text=nome_str, bold=True, size_hint_y=None, height=25, background_color=(0.85, 0.85, 0.85, 1), color=(0, 0, 0, 1), halign='left')
                btn_nome.bind(size=lambda s, w: setattr(s, 'text_size', (s.width - 10, s.height)))
                btn_nome.bind(on_press=lambda instance, pid=p_id: self.seleziona_prodotto(pid))
                top_card.add_widget(btn_nome)
                card_box.add_widget(top_card)

                info_testo = f"Lotto: {lotto_str} | Prezzo: CHF {prezzo_val:.2f} | Giac: {giac_val}\nBar: {barcode_str}"
                btn_dett = Button(text=info_testo, font_size=11, size_hint_y=None, height=60, background_color=(0.92, 0.92, 0.92, 1), color=(0, 0, 0, 1), halign='left', valign='middle')
                btn_dett.bind(size=lambda s, w: setattr(s, 'text_size', (s.width - 10, s.height)))
                btn_dett.bind(on_press=lambda instance, pid=p_id: self.seleziona_prodotto(pid))
                card_box.add_widget(btn_dett)

                self.layout_lista_prodotti.add_widget(card_box)

    def seleziona_tutti(self, instance):
        self.chk_master.active = True
        for chk in self.checkboxes_prodotti.values():
            chk.active = True

    def deseleziona_tutti(self, instance):
        self.chk_master.active = False
        for chk in self.checkboxes_prodotti.values():
            chk.active = False

    def seleziona_prodotto(self, prodotto_id):
        self.prodotto_selezionato_id = prodotto_id
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT codice_barra, nome, categoria, categoria_pos, prezzo, giacenza, lotto, data_scadenza, colore_pulsante, foto_path FROM prodotti WHERE id = ?", (prodotto_id,))
        p = cursor.fetchone()
        conn.close()

        if p:
            self.input_barcode.text = str(p[0] or '')
            self.input_nome.text = str(p[1] or '')
            cat_val = str(p[2] or '')
            self.spinner_categoria.text = cat_val if cat_val else 'Seleziona o scrivi...'
            cat_pos_val = str(p[3] or '')
            self.spinner_categoria_pos.text = cat_pos_val if cat_pos_val else 'Seleziona...'
            self.input_prezzo.text = str(p[4] or 0.0)
            self.input_giacenza.text = str(p[5] or 0.0)
            lotto_val = str(p[6] or '')
            self.spinner_lotto.text = lotto_val if lotto_val else 'Seleziona o scrivi...'
            self.input_scadenza.text = str(p[7] or '')
            self.input_colore.text = str(p[8] or '#333333')
            self.input_foto.text = str(p[9] or '')

    def salva_prodotto(self, instance):
        try:
            barcode = self.input_barcode.text.strip()
            nome = self.input_nome.text.strip()
            categoria = self.spinner_categoria.text.strip()
            if categoria == 'Seleziona o scrivi...':
                categoria = ''
            categoria_pos = self.spinner_categoria_pos.text.strip()
            if categoria_pos == 'Seleziona...':
                categoria_pos = ''
            prezzo = float(self.input_prezzo.text.strip() or 0.0)
            giacenza = float(self.input_giacenza.text.strip() or 0.0)
            lotto = self.spinner_lotto.text.strip()
            if lotto == 'Seleziona o scrivi...':
                lotto = ''
            data_scadenza = self.input_scadenza.text.strip()
            colore_pulsante = self.input_colore.text.strip() or '#333333'
            foto_path = self.input_foto.text.strip()

            if not nome:
                self.mostra_popup('Attenzione', 'Il nome del prodotto è obbligatorio.')
                return

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            if self.prodotto_selezionato_id:
                cursor.execute("""
                    UPDATE prodotti 
                    SET codice_barra=?, nome=?, categoria=?, categoria_pos=?, prezzo=?, giacenza=?, lotto=?, data_scadenza=?, colore_pulsante=?, foto_path=? 
                    WHERE id=?
                """, (barcode, nome, categoria, categoria_pos, prezzo, giacenza, lotto, data_scadenza, colore_pulsante, foto_path, self.prodotto_selezionato_id))
            else:
                cursor.execute("""
                    INSERT INTO prodotti (codice_barra, nome, categoria, categoria_pos, prezzo, giacenza, lotto, data_scadenza, colore_pulsante, foto_path) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (barcode, nome, categoria, categoria_pos, prezzo, giacenza, lotto, data_scadenza, colore_pulsante, foto_path))

            conn.commit()
            conn.close()
            self.aggiorna_spinner_filtro()
            self.aggiorna_lista_prodotti()
            self.mostra_popup('Successo', 'Prodotto salvato con successo!')
        except Exception as e:
            self.mostra_popup('Errore', str(e))

        try:
            ids_selezionati = [pid for pid, chk in self.checkboxes_prodotti.items() if chk.active]
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            if ids_selezionati:
                cursor.executemany("DELETE FROM prodotti WHERE id=?", [(pid,) for pid in ids_selezionati])
                msg = f"Eliminati {len(ids_selezionati)} prodotti selezionati."
            elif self.prodotto_selezionato_id:
                cursor.execute("DELETE FROM prodotti WHERE id=?", (self.prodotto_selezionato_id,))
                msg = "Prodotto corrente eliminato."
                self.prodotto_selezionato_id = None
            else:
                self.mostra_popup('Attenzione', 'Seleziona almeno un prodotto o spunta i checkbox.')
                conn.close()
                return

            conn.commit()
            conn.close()
            self.aggiorna_spinner_filtro()
            self.aggiorna_lista_prodotti()
            self.mostra_popup('Successo', msg)
        except Exception as e:
            self.mostra_popup('Errore', str(e))

        try:
            ids_selezionati = [pid for pid, chk in self.checkboxes_prodotti.items() if chk.active]
            path = esporta_magazzino_excel(ids_selezionati if ids_selezionati else None)
            msg = f"Esportazione completata ({len(ids_selezionati)} articoli selezionati) in: {path}" if ids_selezionati else f"Catalogo completo esportato in: {path}"
            self.mostra_popup('Successo', msg)
        except Exception as e:
            self.mostra_popup('Errore', str(e))

        from kivy.utils import platform
        if platform == 'android':
            from plyer import filechooser
            filechooser.open_file(on_selection=self._on_file_selected)
        else:
            import subprocess
            try:
                file_path = subprocess.check_output(['zenity', '--file-selection'], text=True).strip()
                if file_path:
                    self._on_file_selected([file_path])
            except Exception as e:
                print(f"Errore nella selezione file: {e}")

        try:
            ids_selezionati = [pid for pid, chk in self.checkboxes_prodotti.items() if chk.active]
            path = esporta_magazzino_excel(ids_selezionati if ids_selezionati else None)
            msg = f"Esportazione completata ({len(ids_selezionati)} articoli selezionati) in: {path}" if ids_selezionati else f"Catalogo completo esportato in: {path}"
            self.mostra_popup('Successo', msg)
        except Exception as e:
            self.mostra_popup('Errore', str(e))

        from kivy.utils import platform
        if platform == 'android':
            from plyer import filechooser
            filechooser.open_file(on_selection=self._on_file_selected)
        else:
            import subprocess
            try:
                file_path = subprocess.check_output(['zenity', '--file-selection'], text=True).strip()
                if file_path:
                    self._on_file_selected([file_path])
            except Exception as e:
                print(f"Errore nella selezione file: {e}")

    def elimina_prodotto(self, instance):
        try:
            ids_selezionati = [pid for pid, chk in self.checkboxes_prodotti.items() if chk.active]
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            if ids_selezionati:
                cursor.executemany("DELETE FROM prodotti WHERE id=?", [(pid,) for pid in ids_selezionati])
                msg = f"Eliminati {len(ids_selezionati)} prodotti selezionati."
            elif self.prodotto_selezionato_id:
                cursor.execute("DELETE FROM prodotti WHERE id=?", (self.prodotto_selezionato_id,))
                msg = "Prodotto corrente eliminato."
                self.prodotto_selezionato_id = None
            else:
                self.mostra_popup('Attenzione', 'Seleziona almeno un prodotto o spunta i checkbox.')
                conn.close()
                return

            conn.commit()
            conn.close()
            self.aggiorna_spinner_filtro()
            self.aggiorna_lista_prodotti()
            self.mostra_popup('Successo', msg)
        except Exception as e:
            self.mostra_popup('Errore', str(e))

    def esporta_dati(self, instance):
        try:
            ids_selezionati = [pid for pid, chk in self.checkboxes_prodotti.items() if chk.active]
            path = esporta_magazzino_excel(ids_selezionati if ids_selezionati else None)
            msg = f"Esportazione completata ({len(ids_selezionati)} articoli selezionati) in: {path}" if ids_selezionati else f"Catalogo completo esportato in: {path}"
            self.mostra_popup('Successo', msg)
        except Exception as e:
            self.mostra_popup('Errore', str(e))

    def importa_dati(self, instance):
        from kivy.utils import platform
        if platform == 'android':
            from plyer import filechooser
            filechooser.open_file(on_selection=self._on_file_selected)
        else:
            import subprocess
            try:
                file_path = subprocess.check_output(['zenity', '--file-selection'], text=True).strip()
                if file_path:
                    self._on_file_selected([file_path])
            except Exception as e:
                print(f"Errore nella selezione file: {e}")

    def seleziona_immagine(self, instance):
        from kivy.uix.popup import Popup
        from kivy.uix.filechooser import FileChooserListView
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        import os

        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        filechooser = FileChooserListView(path=os.getcwd(), filters=['*.png', '*.jpg', '*.jpeg'])
        content.add_widget(filechooser)

        btn_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        btn_seleziona = Button(text='Seleziona', background_color=(0.1, 0.4, 0.7, 1))
        btn_chiudi = Button(text='Annulla', background_color=(0.5, 0.5, 0.5, 1))
        
        btn_layout.add_widget(btn_seleziona)
        btn_layout.add_widget(btn_chiudi)
        content.add_widget(btn_layout)

        popup = Popup(title='Seleziona un immagine', content=content, size_hint=(0.8, 0.8))

        def on_选择(btn):
            if filechooser.selection:
                self._on_image_selected(filechooser.selection)
            popup.dismiss()

        btn_seleziona.bind(on_press=on_选择)
        btn_chiudi.bind(on_press=popup.dismiss)
        popup.open()

    def _on_image_selected(self, selection):
        if selection and len(selection) > 0:
            path_img = selection[0]
            self.input_foto.text = path_img
            # Aggiorniamo il pulsante o l'anteprima foto
        if hasattr(self, 'btn_anteprima_foto'):
            self.btn_anteprima_foto.background_normal = path_img
            self.btn_anteprima_foto.text = ''
        if hasattr(self, 'img_preview'):
                self.img_preview.source = path_img
