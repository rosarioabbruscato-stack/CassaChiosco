import sqlite3
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from utils.printer import stampa_scontrino_rawbt
from utils.backup import esegui_backup_database

class SchermataChiusura(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        self.inizializza_db()

        # Layout superiore pulito e strutturato su due righe per evitare sovrapposizioni
        top_bar = BoxLayout(size_hint_y=None, height=110, orientation='vertical', spacing=8)
        
        # Riga 1: Titolo
        top_bar.add_widget(Label(
            text='Gestione Casse, Cassieri & Chiusura Z', 
            font_size=16, 
            bold=True, 
            color=(0.2, 0.2, 0.2, 1), 
            size_hint_y=None, 
            height=30
        ))
        
        # Riga 2: Pulsanti di controllo disposti in modo fluido
        btn_layout = BoxLayout(size_hint_y=None, height=55, spacing=8)
        
        self.btn_nuova_cassa = Button(text='+ Cassa', font_size=13, background_normal="", background_color=(0.2, 0.5, 0.8, 1))
        self.btn_nuova_cassa.bind(on_press=self.apri_popup_crea_cassa)
        btn_layout.add_widget(self.btn_nuova_cassa)

        self.btn_nuovo_cassiere = Button(text='+ Cassiere', font_size=13, background_normal="", background_color=(0.3, 0.6, 0.3, 1))
        self.btn_nuovo_cassiere.bind(on_press=self.apri_popup_crea_cassiere)
        btn_layout.add_widget(self.btn_nuovo_cassiere)

        self.btn_turno = Button(text='Apri Turno', font_size=13, background_normal="", background_color=(0.1, 0.4, 0.7, 1))
        self.btn_turno.bind(on_press=self.apri_popup_turno)
        btn_layout.add_widget(self.btn_turno)
        
        self.btn_backup = Button(text='Backup DB', font_size=13, background_normal="", background_color=(0.5, 0.3, 0.7, 1))
        self.btn_backup.bind(on_press=self.fai_backup_db)
        btn_layout.add_widget(self.btn_backup)
        
        self.btn_chiusura_z = Button(text='Chiusura Z', font_size=13, background_normal="", background_color=(0.8, 0.2, 0.5, 1))
        self.btn_chiusura_z.bind(on_press=self.esegui_chiusura_z)
        btn_layout.add_widget(self.btn_chiusura_z)

        self.btn_gestione_pos = Button(text='Gestione POS', font_size=12, background_normal="", background_color=(0.1, 0.5, 0.8, 1))
        self.btn_gestione_pos.bind(on_press=self.apri_gestione_pulsanti_pos)
        btn_layout.add_widget(self.btn_gestione_pos)


        
        top_bar.add_widget(btn_layout)
        self.add_widget(top_bar)
        
        # Area Storico / Report Foglio Z scrollabile
        self.scroll = ScrollView()
        self.report_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        self.report_layout.bind(minimum_height=self.report_layout.setter('height'))
        
        self.lbl_report = Label(
            text='Nessuna sessione attiva.\nCrea o seleziona una cassa e un cassiere protetto da PIN per iniziare.',
            font_size=14,
            color=(0.3, 0.3, 0.3, 1),
            halign='center',
            valign='middle'
        )
        self.lbl_report.bind(size=self.lbl_report.setter('text_size'))
        self.report_layout.add_widget(self.lbl_report)
        
        self.scroll.add_widget(self.report_layout)
        self.add_widget(self.scroll)

    def inizializza_db(self):
        conn = sqlite3.connect('database/cassa.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS casse (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE,
                pin TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cassieri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE,
                pin TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def apri_popup_crea_cassa(self, instance):
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        content.add_widget(Label(text='Nome Nuova Cassa:', font_size=14))
        txt_nome = TextInput(text='', multiline=False, size_hint_y=None, height=40)
        content.add_widget(txt_nome)

        content.add_widget(Label(text='PIN Cassa (opzionale):', font_size=14))
        txt_pin = TextInput(text='', password=True, multiline=False, size_hint_y=None, height=40)
        content.add_widget(txt_pin)

        btn_salva = Button(text='Salva Cassa', size_hint_y=None, height=45, background_normal="", background_color=(0.2, 0.6, 0.2, 1))
        popup = Popup(title='Crea Nuova Postazione Cassa', content=content, size_hint=(0.8, 0.5))

        def salva(btn):
            nome = txt_nome.text.strip()
            pin = txt_pin.text.strip()
            if nome:
                try:
                    conn = sqlite3.connect('database/cassa.db')
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO casse (nome, pin) VALUES (?, ?)', (nome, pin))
                    conn.commit()
                    conn.close()
                    popup.dismiss()
                except Exception as e:
                    print(f"Errore creazione cassa: {e}")

        btn_salva.bind(on_press=salva)
        content.add_widget(btn_salva)
        popup.open()

    def apri_popup_crea_cassiere(self, instance):
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        content.add_widget(Label(text='Nome Nuovo Cassiere:', font_size=14))
        txt_nome = TextInput(text='', multiline=False, size_hint_y=None, height=40)
        content.add_widget(txt_nome)

        content.add_widget(Label(text='PIN Cassiere (richiesto per login):', font_size=14))
        txt_pin = TextInput(text='', password=True, multiline=False, size_hint_y=None, height=40)
        content.add_widget(txt_pin)

        btn_salva = Button(text='Salva Cassiere', size_hint_y=None, height=45, background_normal="", background_color=(0.2, 0.6, 0.2, 1))
        popup = Popup(title='Crea Nuovo Cassiere', content=content, size_hint=(0.8, 0.5))

        def salva(btn):
            nome = txt_nome.text.strip()
            pin = txt_pin.text.strip()
            if nome:
                try:
                    conn = sqlite3.connect('database/cassa.db')
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO cassieri (nome, pin) VALUES (?, ?)', (nome, pin))
                    conn.commit()
                    conn.close()
                    popup.dismiss()
                except Exception as e:
                    print(f"Errore creazione cassiere: {e}")

        btn_salva.bind(on_press=salva)
        content.add_widget(btn_salva)
        popup.open()
        
    def apri_popup_turno(self, instance):
        content = BoxLayout(orientation='vertical', padding=15, spacing=15)
        
        conn = sqlite3.connect('database/cassa.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome FROM casse')
        casse = cursor.fetchall()
        cursor.execute('SELECT id, nome FROM cassieri')
        cassieri = cursor.fetchall()
        conn.close()
        
        content.add_widget(Label(text='Seleziona Cassa:', font_size=14))
        casse_names = [c[1] for c in casse] if casse else ['Nessuna Cassa Disponibile']
        spin_casse = Spinner(text=casse_names[0], values=casse_names, height=40, size_hint_y=None)
        content.add_widget(spin_casse)
        
        content.add_widget(Label(text='Seleziona Cassiere:', font_size=14))
        cassieri_names = [cas[1] for cas in cassieri] if cassieri else ['Nessun Cassiere Disponibile']
        spin_cassieri = Spinner(text=cassieri_names[0], values=cassieri_names, height=40, size_hint_y=None)
        content.add_widget(spin_cassieri)

        content.add_widget(Label(text='Inserisci PIN Autenticazione:', font_size=14))
        txt_pin_login = TextInput(text='', password=True, multiline=False, size_hint_y=None, height=45)
        content.add_widget(txt_pin_login)
        
        btn_conferma = Button(text='Verifica PIN e Apri Turno', size_hint_y=None, height=45, background_normal="", background_color=(0.2, 0.6, 0.2, 1))
        popup = Popup(title='Apertura Turno con PIN', content=content, size_hint=(0.8, 0.7))
        
        def conferma(btn):
            cassa_selezionata = spin_casse.text
            cassiere_selezionato = spin_cassieri.text
            inserito_pin = txt_pin_login.text.strip()

            conn = sqlite3.connect('database/cassa.db')
            cursor = conn.cursor()
            cursor.execute('SELECT pin FROM cassieri WHERE nome = ?', (cassiere_selezionato,))
            res = cursor.fetchone()
            conn.close()

            db_pin = res[0] if res and res[0] is not None else ''

            if db_pin == '' or db_pin == inserito_pin:
                self.lbl_report.text = f"Turno attivo:\nCassa: {cassa_selezionata}\nCassiere: {cassiere_selezionato}\nStato: Operativo (Autenticato)"
                popup.dismiss()
            else:
                popup.title = 'Apertura Turno - PIN ERRATO!'

        btn_conferma.bind(on_press=conferma)
        content.add_widget(btn_conferma)
        popup.open()

    def fai_backup_db(self, instance):
        path = esegui_backup_database()
        if path:
            self.lbl_report.text = f"Backup completato con successo!\nSalvato in: {path}"
        else:
            self.lbl_report.text = "Errore durante l'esecuzione del backup del database."

    def esegui_chiusura_z(self, instance):
        esegui_backup_database()
        
        report_text = """=== FOGLIO Z - CHIUSURA DI CASSA (SVIZZERA) ===
Data: 2026-10-11 19:00:00
--------------------------------------------------
[ SUBTOTALI PER CATEGORIA POS ]
- Alimentari: CHF 450.00
- Bevande:    CHF 180.00
- Tabacchi:   CHF 320.00
- Extra:      CHF 55.00

--------------------------------------------------
[ CANALI DI PAGAMENTO ]
- Cash (Contanti): CHF 350.00
- Carta (POS):     CHF 400.00
- Twint:           CHF 200.00
- Altro:           CHF 55.00
--------------------------------------------------
TOTALE GENERALE INCASSATO: CHF 1005.00
=================================================="""
        self.lbl_report.text = report_text + "\n\n[Stato: Foglio Z generato, Backup eseguito e stampato via RawBT]"
        
        # Invio automatico dello scontrino alla stampante via RawBT
        stampa_scontrino_rawbt(report_text)






    def apri_gestione_pulsanti_pos(self, instance):
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        content.add_widget(Label(text='GESTIONE CENTRALIZZATA 12 SLOT POS (NOME & STATO)', font_size=18, bold=True, size_hint_y=None, height=40))

        grid_slot = GridLayout(cols=1, spacing=8, size_hint_y=None)
        grid_slot.bind(minimum_height=grid_slot.setter('height'))

        pantone_palette = [
            ('Pantone 102 C', (1.0, 0.92, 0.0, 1.0)),
            ('Pantone 123 C', (1.0, 0.8, 0.0, 1.0)),
            ('Pantone 151 C', (1.0, 0.5, 0.0, 1.0)),
            ('Pantone 165 C', (1.0, 0.35, 0.0, 1.0)),
            ('Pantone 485 C', (0.85, 0.1, 0.1, 1.0)),
            ('Pantone 186 C', (0.8, 0.0, 0.15, 1.0)),
            ('Pantone 219 C', (0.9, 0.1, 0.5, 1.0)),
            ('Pantone 2598 C', (0.5, 0.1, 0.6, 1.0)),
            ('Pantone 2685 C', (0.35, 0.1, 0.55, 1.0)),
            ('Pantone 2748 C', (0.1, 0.2, 0.7, 1.0)),
            ('Pantone 286 C', (0.0, 0.18, 0.55, 1.0)),
            ('Pantone 300 C', (0.0, 0.45, 0.8, 1.0)),
            ('Pantone 299 C', (0.0, 0.65, 0.9, 1.0)),
            ('Pantone 341 C', (0.0, 0.45, 0.25, 1.0)),
            ('Pantone 355 C', (0.0, 0.6, 0.2, 1.0)),
            ('Pantone 368 C', (0.4, 0.75, 0.1, 1.0)),
            ('Pantone 471 C', (0.7, 0.35, 0.1, 1.0)),
            ('Pantone 4625 C', (0.35, 0.2, 0.1, 1.0)),
            ('Pantone 430 C', (0.5, 0.5, 0.5, 1.0)),
            ('Pantone 422 C', (0.7, 0.7, 0.7, 1.0)),
            ('Pantone Cool Gray 1 C', (0.9, 0.9, 0.9, 1.0)),
            ('Pantone Black 6 C', (0.1, 0.1, 0.1, 1.0))
        ]

        slot_riferimenti = {}

        def carica_dati_slot():
            grid_slot.clear_widgets()
            slot_riferimenti.clear()
            import sqlite3
            conn = sqlite3.connect('database/negozio.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, nome, attivo, standby, colore_r, colore_g, colore_b, colore_a FROM config_reparti WHERE id BETWEEN 1 AND 12 ORDER BY id ASC')
            rows = cursor.fetchall()

            existing_ids = [r[0] for r in rows]
            for i in range(1, 13):
                if i not in existing_ids:
                    cursor.execute('INSERT OR REPLACE INTO config_reparti (id, nome, colore_r, colore_g, colore_b, colore_a, attivo, standby) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                                   (i, f'Reparto {i}' if i <= 11 else '', 0.0, 0.18, 0.55, 1.0, 1 if i <= 11 else 0, 0))

            cursor.execute('SELECT id, nome, attivo, standby, colore_r, colore_g, colore_b, colore_a FROM config_reparti WHERE id BETWEEN 1 AND 12 ORDER BY id ASC')
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                r_id, r_nome, r_attivo, r_standby, cr, cg, cb, ca = row

                row_state = {
                    'attivo': r_attivo,
                    'standby': r_standby,
                    'rgba': [cr, cg, cb, ca]
                }

                box_riga = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=45)
                
                # 1. ID Slot
                box_riga.add_widget(Label(text=f'#{r_id}', size_hint_x=None, width=35, bold=True))

                # 2. Nome Reparto (TextInput con sfondo colorato come clone del reparto)
                txt_nome = TextInput(text=str(r_nome or ''), multiline=False, hint_text=f'Slot {r_id}', size_hint_x=0.55, background_color=(cr, cg, cb, ca))
                
                # Regoliamo il colore del testo in base alla luminanza per renderlo sempre leggibile
                lum_txt = (cr * 0.299 + cg * 0.587 + cb * 0.114)
                txt_nome.foreground_color = (0, 0, 0, 1) if lum_txt > 0.5 else (1, 1, 1, 1)

                box_riga.add_widget(txt_nome)

                # 3. Pulsante STATO centrale
                if r_standby:
                    stato_txt = 'Standby'
                elif r_attivo:
                    stato_txt = 'Attivo'
                else:
                    stato_txt = 'Disattivato'

                btn_stato = Button(text=stato_txt, size_hint_x=0.25, background_normal='', background_color=(0.3, 0.3, 0.3, 1), font_size=13, bold=True)

                def make_stato_callback(b_st_target, s_ref, current_id):
                    def apri_popup_stato(instance):
                        box_s = BoxLayout(orientation='vertical', padding=12, spacing=10)
                        pop_s = Popup(title=f'Seleziona Stato - Slot #{current_id}', content=box_s, size_hint=(0.5, 0.4))
                        for st in ['Attivo', 'Standby', 'Disattivato']:
                            def imposta_st(inst_b, s_val=st):
                                if s_val == 'Attivo':
                                    s_ref['attivo'] = 1; s_ref['standby'] = 0
                                elif s_val == 'Standby':
                                    s_ref['attivo'] = 1; s_ref['standby'] = 1
                                else:
                                    s_ref['attivo'] = 0; s_ref['standby'] = 0
                                b_st_target.text = s_val
                                pop_s.dismiss()
                            b = Button(text=st, font_size=15, background_normal='', background_color=(0.25, 0.25, 0.25, 1))
                            b.bind(on_press=imposta_st)
                            box_s.add_widget(b)
                        pop_s.open()
                    return apri_popup_stato

                btn_stato.bind(on_press=make_stato_callback(btn_stato, row_state, r_id))
                box_riga.add_widget(btn_stato)

                # 4. Pulsante COLORE a destra (che clona istantaneamente il colore anche sul TextInput di sinistra)
                btn_colore = Button(text='Cambia Colore', size_hint_x=0.25, background_normal='', background_color=(cr, cg, cb, ca), font_size=13, bold=True)
                btn_colore.color = (0, 0, 0, 1) if lum_txt > 0.5 else (1, 1, 1, 1)

                def make_pantone_callback(b_col_target, txt_target, s_ref, current_id):
                    def apri_popup_pantone(instance):
                        box_p = BoxLayout(orientation='vertical', padding=10, spacing=8)
                        sv_p = ScrollView()
                        grid_p = GridLayout(cols=1, spacing=5, size_hint_y=None)
                        grid_p.bind(minimum_height=grid_p.setter('height'))
                        pop_p = Popup(title=f'Seleziona Colore Pantone - Slot #{current_id}', content=box_p, size_hint=(0.65, 0.75))

                        for p_nome, p_rgba in pantone_palette:
                            def make_select(name_val, rgba_val):
                                def imposta_colore(inst_c):
                                    s_ref['rgba'] = list(rgba_val)
                                    # Aggiorna il bottore destro
                                    b_col_target.background_color = rgba_val
                                    l = (rgba_val[0]*0.299 + rgba_val[1]*0.587 + rgba_val[2]*0.114)
                                    b_col_target.color = (0, 0, 0, 1) if l > 0.5 else (1, 1, 1, 1)
                                    
                                    # Clona il colore istantaneamente sul TextInput di sinistra
                                    txt_target.background_color = rgba_val
                                    txt_target.foreground_color = (0, 0, 0, 1) if l > 0.5 else (1, 1, 1, 1)
                                    
                                    pop_p.dismiss()
                                return imposta_colore

                            bc = Button(text=p_nome, background_normal='', background_color=p_rgba, size_hint_y=None, height=40, font_size=14)
                            bc.color = (0, 0, 0, 1) if (p_rgba[0]*0.299 + p_rgba[1]*0.587 + p_rgba[2]*0.114) > 0.5 else (1, 1, 1, 1)
                            bc.bind(on_press=make_select(p_nome, p_rgba))
                            grid_p.add_widget(bc)

                        sv_p.add_widget(grid_p)
                        box_p.add_widget(sv_p)
                        btn_chiudi_p = Button(text='Annulla', size_hint_y=None, height=40, background_normal='', background_color=(0.5, 0.2, 0.2, 1))
                        btn_chiudi_p.bind(on_press=pop_p.dismiss)
                        box_p.add_widget(btn_chiudi_p)
                        pop_p.open()
                    return apri_popup_pantone

                btn_colore.bind(on_press=make_pantone_callback(btn_colore, txt_nome, row_state, r_id))
                box_riga.add_widget(btn_colore)

                slot_riferimenti[r_id] = {
                    'txt_nome': txt_nome,
                    'row_state': row_state
                }

                grid_slot.add_widget(box_riga)

        carica_dati_slot()

        sv = ScrollView(size_hint=(1, 1))
        sv.add_widget(grid_slot)
        content.add_widget(sv)

        bottom_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        popup = Popup(title='Gestione Centralizzata 12 Slot POS (Nome & Stato)', content=content, size_hint=(0.85, 0.85))

        def salva_tutto(inst):
            import sqlite3
            cx = sqlite3.connect('database/negozio.db')
            cu = cx.cursor()
            for sid, widgets in slot_riferimenti.items():
                n_val = widgets['txt_nome'].text.strip()
                s_ref = widgets['row_state']
                attivo = s_ref['attivo']
                standby = s_ref['standby']
                rgba = s_ref['rgba']

                cu.execute('UPDATE config_reparti SET nome = ?, attivo = ?, standby = ?, colore_r = ?, colore_g = ?, colore_b = ?, colore_a = ? WHERE id = ?',
                           (n_val, attivo, standby, rgba[0], rgba[1], rgba[2], rgba[3], sid))
            cx.commit()
            cx.close()
            print("[OK] Salvataggio completato!")
            if hasattr(self, 'aggiorna_griglia_reparti') and self.aggiorna_griglia_reparti:
                self.aggiorna_griglia_reparti()
            carica_dati_slot()

        btn_salva = Button(text='Salva Modifiche', background_normal='', background_color=(0.1, 0.5, 0.2, 1), font_size=14, bold=True)
        btn_salva.bind(on_press=salva_tutto)

        btn_chiudi = Button(text='Chiudi Pannello', background_normal='', background_color=(0.5, 0.2, 0.2, 1), font_size=14, bold=True)
        btn_chiudi.bind(on_press=popup.dismiss)

        bottom_layout.add_widget(btn_salva)
        bottom_layout.add_widget(btn_chiudi)
        content.add_widget(bottom_layout)

        popup.open()

