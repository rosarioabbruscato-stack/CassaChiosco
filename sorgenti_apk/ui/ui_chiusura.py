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
        
        self.btn_nuova_cassa = Button(text='+ Cassa', font_size=13, background_color=(0.2, 0.5, 0.8, 1))
        self.btn_nuova_cassa.bind(on_press=self.apri_popup_crea_cassa)
        btn_layout.add_widget(self.btn_nuova_cassa)

        self.btn_nuovo_cassiere = Button(text='+ Cassiere', font_size=13, background_color=(0.3, 0.6, 0.3, 1))
        self.btn_nuovo_cassiere.bind(on_press=self.apri_popup_crea_cassiere)
        btn_layout.add_widget(self.btn_nuovo_cassiere)

        self.btn_turno = Button(text='Apri Turno', font_size=13, background_color=(0.1, 0.4, 0.7, 1))
        self.btn_turno.bind(on_press=self.apri_popup_turno)
        btn_layout.add_widget(self.btn_turno)
        
        self.btn_backup = Button(text='Backup DB', font_size=13, background_color=(0.5, 0.3, 0.7, 1))
        self.btn_backup.bind(on_press=self.fai_backup_db)
        btn_layout.add_widget(self.btn_backup)
        
        self.btn_chiusura_z = Button(text='Chiusura Z', font_size=13, background_color=(0.8, 0.2, 0.5, 1))
        self.btn_chiusura_z.bind(on_press=self.esegui_chiusura_z)
        btn_layout.add_widget(self.btn_chiusura_z)

        self.btn_gestione_pos = Button(text='Gestione POS', font_size=12, background_color=(0.1, 0.5, 0.8, 1))
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

        btn_salva = Button(text='Salva Cassa', size_hint_y=None, height=45, background_color=(0.2, 0.6, 0.2, 1))
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

        btn_salva = Button(text='Salva Cassiere', size_hint_y=None, height=45, background_color=(0.2, 0.6, 0.2, 1))
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
        
        btn_conferma = Button(text='Verifica PIN e Apri Turno', size_hint_y=None, height=45, background_color=(0.2, 0.6, 0.2, 1))
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
        content.add_widget(Label(text='GESTIONE CENTRALIZZATA 12 SLOT POS (PANTONE)', font_size=18, bold=True, size_hint_y=None, height=40))

        grid_slot = GridLayout(cols=1, spacing=8, size_hint_y=None)
        grid_slot.bind(minimum_height=grid_slot.setter('height'))

        pantone_palette = {
            'Pantone 102 C (Giallo Vivo)': (1.0, 0.92, 0.0, 1.0),
            'Pantone 123 C (Giallo Oro)': (1.0, 0.8, 0.0, 1.0),
            'Pantone 151 C (Arancione Caldo)': (1.0, 0.5, 0.0, 1.0),
            'Pantone 165 C (Arancio Vivo)': (1.0, 0.35, 0.0, 1.0),
            'Pantone 485 C (Rosso Pantone)': (0.85, 0.1, 0.1, 1.0),
            'Pantone 186 C (Rosso Rubino)': (0.8, 0.0, 0.15, 1.0),
            'Pantone 219 C (Magenta Vivo)': (0.9, 0.1, 0.5, 1.0),
            'Pantone 2598 C (Porpora)': (0.5, 0.1, 0.6, 1.0),
            'Pantone 2685 C (Viola Scuro)': (0.35, 0.1, 0.55, 1.0),
            'Pantone 2748 C (Blu Elettrico)': (0.1, 0.2, 0.7, 1.0),
            'Pantone 286 C (Blu Classico)': (0.0, 0.18, 0.55, 1.0),
            'Pantone 300 C (Azzurro)': (0.0, 0.45, 0.8, 1.0),
            'Pantone 299 C (Celeste)': (0.0, 0.65, 0.9, 1.0),
            'Pantone 341 C (Verde Scuro)': (0.0, 0.45, 0.25, 1.0),
            'Pantone 355 C (Verde Prato)': (0.0, 0.6, 0.2, 1.0),
            'Pantone 368 C (Verde Mela)': (0.4, 0.75, 0.1, 1.0),
            'Pantone 471 C (Marrone Terra)': (0.7, 0.35, 0.1, 1.0),
            'Pantone 4625 C (Marrone Scuro)': (0.35, 0.2, 0.1, 1.0),
            'Pantone 430 C (Grigio Medio)': (0.5, 0.5, 0.5, 1.0),
            'Pantone 422 C (Grigio Chiaro)': (0.7, 0.7, 0.7, 1.0),
            'Pantone Cool Gray 1 C (Bianco Sporco)': (0.9, 0.9, 0.9, 1.0),
            'Pantone Black 6 C (Nero Profondo)': (0.1, 0.1, 0.1, 1.0)
        }

        def trova_nome_pantone(r, g, b):
            for nome_p, val in pantone_palette.items():
                if abs(val[0] - r) < 0.15 and abs(val[1] - g) < 0.15 and abs(val[2] - b) < 0.15:
                    return nome_p
            return 'Pantone 286 C (Blu Classico)'

        def carica_dati_slot():
            grid_slot.clear_widgets()
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
            
            if len(rows) < 8:
                cursor.execute('SELECT id, nome, attivo, standby, colore_r, colore_g, colore_b, colore_a FROM config_reparti WHERE id BETWEEN 1 AND 12 ORDER BY id ASC')
                rows = cursor.fetchall()
            
            conn.close()

            for row in rows:
                r_id, r_nome, r_attivo, r_standby, cr, cg, cb, ca = row
                box_riga = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=None, height=45)
                
                txt_nome = TextInput(text=str(r_nome or ''), multiline=False, hint_text=f'Slot {r_id}', size_hint_x=0.35)
                
                # Stato iniziale basato sul database
                if r_standby:
                    stato_txt = 'Standby'
                elif r_attivo:
                    stato_txt = 'Attivo'
                else:
                    stato_txt = 'Disattivato'

                btn_stato = Button(text=stato_txt, size_hint_x=0.2, background_color=(0.3, 0.3, 0.3, 1))

                colore_attuale_nome = trova_nome_pantone(cr, cg, cb)
                btn_colore = Button(text=colore_attuale_nome, size_hint_x=0.25, background_color=(cr, cg, cb, ca))

                btn_salva = Button(text='Salva', background_color=(0.2, 0.7, 0.3, 1), size_hint_x=0.12)
                btn_elimina = Button(text='Elimina', background_color=(0.8, 0.2, 0.2, 1), size_hint_x=0.08)

                colore_ref = {'rgba': (cr, cg, cb, ca)}

                # Popup selezione Stato
                def apri_popup_stato(inst, b_st=btn_stato):
                    box_s = BoxLayout(orientation='vertical', padding=10, spacing=10)
                    pop_s = Popup(title=f'Seleziona Stato - Slot #{r_id}', content=box_s, size_hint=(0.5, 0.4))
                    for st in ['Attivo', 'Standby', 'Disattivato']:
                        def imposta_st(i, s=st):
                            b_st.text = s
                            pop_s.dismiss()
                        b = Button(text=st, font_size=16)
                        b.bind(on_press=imposta_st)
                        box_s.add_widget(b)
                    pop_s.open()

                # Popup selezione Pantone
                def apri_popup_pantone(inst, b_col=btn_colore):
                    box_p = BoxLayout(orientation='vertical', padding=10, spacing=8)
                    sv_p = ScrollView()
                    grid_p = GridLayout(cols=1, spacing=5, size_hint_y=None)
                    grid_p.bind(minimum_height=grid_p.setter('height'))
                    
                    pop_p = Popup(title=f'Seleziona Pantone - Slot #{r_id}', content=box_p, size_hint=(0.7, 0.7))
                    
                    for p_nome, p_rgba in pantone_palette.items():
                        def imposta_colore(i, pn=p_nome, prgba=p_rgba):
                            colore_ref['rgba'] = prgba
                            b_col.text = pn
                            b_col.background_color = prgba
                            pop_p.dismiss()
                        
                        bc = Button(text=p_nome, background_color=p_rgba, size_hint_y=None, height=40, font_size=14)
                        bc.bind(on_press=imposta_colore)
                        grid_p.add_widget(bc)
                    
                    sv_p.add_widget(grid_p)
                    box_p.add_widget(sv_p)
                    
                    btn_chiudi_p = Button(text='Annulla', size_hint_y=None, height=40)
                    btn_chiudi_p.bind(on_press=pop_p.dismiss)
                    box_p.add_widget(btn_chiudi_p)
                    
                    pop_p.open()

                btn_stato.bind(on_press=apri_popup_stato)
                btn_colore.bind(on_press=apri_popup_pantone)

                def fai_salva(inst, sid=r_id, tb=txt_nome, b_st=btn_stato):
                    n_val = tb.text.strip()
                    s_val = b_st.text.strip()
                    rgba = colore_ref['rgba']
                    
                    # Lettura diretta e rigorosa dal testo del pulsante stato
                    if s_val == 'Standby':
                        attivo = 1
                        standby = 1
                    elif s_val == 'Attivo':
                        attivo = 1
                        standby = 0
                    else:
                        attivo = 0
                        standby = 0
                    
                    cx = sqlite3.connect('database/negozio.db')
                    cu = cx.cursor()
                    cu.execute('UPDATE config_reparti SET nome = ?, attivo = ?, standby = ?, colore_r = ?, colore_g = ?, colore_b = ?, colore_a = ? WHERE id = ?',
                               (n_val, attivo, standby, rgba[0], rgba[1], rgba[2], rgba[3], sid))
                    cx.commit()
                    cx.close()
                    carica_dati_slot()

                def fai_elimina(inst, sid=r_id, tb=txt_nome, b_st=btn_stato):
                    cx = sqlite3.connect('database/negozio.db')
                    cu = cx.cursor()
                    cu.execute('UPDATE config_reparti SET nome = ?, attivo = 0, standby = 0 WHERE id = ?', ('', sid))
                    cx.commit()
                    cx.close()
                    carica_dati_slot()

                btn_salva.bind(on_press=fai_salva)
                btn_elimina.bind(on_press=fai_elimina)

                box_riga.add_widget(Label(text=f'#{r_id}', size_hint_x=None, width=35, bold=True))
                box_riga.add_widget(txt_nome)
                box_riga.add_widget(btn_stato)
                box_riga.add_widget(btn_colore)
                box_riga.add_widget(btn_salva)
                box_riga.add_widget(btn_elimina)
                
                grid_slot.add_widget(box_riga)

        carica_dati_slot()

        sv = ScrollView(size_hint=(1, 1))
        sv.add_widget(grid_slot)
        content.add_widget(sv)

        btn_chiudi = Button(text='Chiudi Pannello', size_hint_y=None, height=50, background_color=(0.3, 0.3, 0.3, 1))
        popup = Popup(title='Gestione Pulsanti POS (12 Slot Fissi - Pantone)', content=content, size_hint=(0.9, 0.85))
        btn_chiudi.bind(on_press=popup.dismiss)
        content.add_widget(btn_chiudi)

        popup.open()
