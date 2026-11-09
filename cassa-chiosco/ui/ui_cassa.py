from ui.ui_chiusura import SchermataChiusura

from ui.ui_magazzino import InterfacciaMagazzino
import sqlite3
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from ui.ui_styles import CustomButton, COLORI_REPARTI
from kivy.metrics import dp


class InterfacciaCassa(BoxLayout):
    def seleziona_reparto(self, nome_reparto):
        print(f"DEBUG: Reparto selezionato: {nome_reparto}")
        if hasattr(self, "lbl_stato_corrente") and self.lbl_stato_corrente:
            self.lbl_stato_corrente.text = f"Reparto selezionato: {nome_reparto}. Inserisci Q.tà o Prezzo."
        self.reparto_corrente = nome_reparto

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.valuta_corrente = "CHF" 
        self.orientation = "vertical"
        self.add_widget(self.crea_menu_superiore(self))
        self.add_widget(self.crea_schermata_vendita(self))
    @staticmethod
    def crea_menu_superiore(app_instance):
        nav_layout = BoxLayout(size_hint_y=None, height=dp(64), padding=0, spacing=10)
        
        btn_vendita = CustomButton(text="Cassa / Vendita", bg_color=(0.3, 0.15, 0.7, 1), bold=True, font_size='14sp')
        btn_vendita.bind(on_press=lambda x: app_instance.mostra_schermata("vendita"))
        
        btn_magazzino = CustomButton(text="Magazzino", bg_color=(0.8, 0.8, 0.8, 1), color=(0.1, 0.1, 0.1, 1), bold=True, font_size='14sp')
        btn_magazzino.bind(on_press=lambda x: app_instance.mostra_schermata("magazzino"))
        
        btn_storico = CustomButton(text="Chiusura & Storico", bg_color=(0.8, 0.8, 0.8, 1), color=(0.1, 0.1, 0.1, 1), bold=True, font_size='14sp')
        btn_storico.bind(on_press=lambda x: app_instance.mostra_schermata("storico"))
        
        nav_layout.add_widget(btn_vendita)
        nav_layout.add_widget(btn_magazzino)
        nav_layout.add_widget(btn_storico)
        return nav_layout

    @staticmethod
    def crea_schermata_vendita(app_instance):
        print('DEBUG: Inizio crea_schermata_vendita')
        layout = BoxLayout(orientation='horizontal', padding=[20, 10, 20, 10], spacing=20)

        # --- COLONNA DI SINISTRA ---
        left_box = BoxLayout(orientation='vertical', padding=[20, 10, 20, 10], spacing=10, size_hint_x=0.48)

        scroll_scontrino = ScrollView()
        app_instance.scontrino_label = Label(text="Scontrino Vuoto", font_name="Roboto", font_size='13sp', halign='left', valign='top', size_hint_y=None, color=(0.2, 0.2, 0.2, 1))
        def update_text_size(instance, width):
            if width > 0 and instance.text_size[0] != width:
                instance.text_size = (width, None)
        def update_height(instance, texture_size):
            if texture_size[1] > 0 and instance.height != texture_size[1]:
                instance.height = texture_size[1]
        
        app_instance.scontrino_label.bind(width=update_text_size)
        app_instance.scontrino_label.bind(texture_size=update_height)
        scroll_scontrino.add_widget(app_instance.scontrino_label)
        left_box.add_widget(scroll_scontrino)

        # Contenitore orizzontale per i due pulsanti affiancati
        layout_due_btn = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)

        app_instance.btn_elimina_riga = CustomButton(
            text='ELIMINA RIGA',
            bg_color=(0.9, 0.25, 0.25, 1),
            size_hint_y=None,
            height=40,
            bold=True,
            font_size='13sp'
        )
        app_instance.btn_elimina_riga.bind(on_press=app_instance.gestisci_azione_scontrino)

        app_instance.btn_stampa_scontrino = CustomButton(
            text='STAMPA',
            bg_color=(0.85, 0.2, 0.2, 1),
            size_hint_y=None,
            height=40,
            bold=True,
            font_size='13sp'
        )
        if hasattr(app_instance, 'stampa_scontrino_manuale'):
            app_instance.btn_stampa_scontrino.bind(on_press=app_instance.stampa_scontrino_manuale)

        layout_due_btn.add_widget(app_instance.btn_elimina_riga)
        layout_due_btn.add_widget(app_instance.btn_stampa_scontrino)
        left_box.add_widget(layout_due_btn)

        app_instance.btn_azione_scontrino = app_instance.btn_elimina_riga

        tot_box = BoxLayout(orientation='vertical', size_hint_y=None, height=50, spacing=2)
        app_instance.lbl_totale = Label(text=f"TOTALE: {app_instance.valuta_corrente} 0.00", font_size='18sp', bold=True, halign='right', color=(0.1, 0.1, 0.1, 1))
        app_instance.lbl_totale.bind(size=app_instance.lbl_totale.setter('text_size'))

        app_instance.lbl_resto = Label(text="Resto: -", font_size='12sp', color=(0.1, 0.65, 0.3, 1), halign='right', bold=True)
        app_instance.lbl_resto.bind(size=app_instance.lbl_resto.setter('text_size'))

        tot_box.add_widget(app_instance.lbl_totale)
        tot_box.add_widget(app_instance.lbl_resto)
        left_box.add_widget(tot_box)

        moneta_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=25, spacing=10)
        lbl_ricevuto = Label(text="Importo Ricevuto:", size_hint_x=0.5, font_size='12sp', color=(0.2, 0.2, 0.2, 1), halign='left')
        lbl_ricevuto.bind(size=lbl_ricevuto.setter('text_size'))
        moneta_box.add_widget(lbl_ricevuto)

        app_instance.input_moneta = TextInput(text="", multiline=False, font_size='13sp', input_filter='float', hint_text="Contanti")
        app_instance.input_moneta.bind(text=app_instance.aggiorna_resto)
        moneta_box.add_widget(app_instance.input_moneta)
        left_box.add_widget(moneta_box)

        lbl_pagamento = Label(text="Seleziona Pagamento:", size_hint_y=None, height=20, font_size='12sp', color=(0.2, 0.2, 0.2, 1), halign='left')
        lbl_pagamento.bind(size=lbl_pagamento.setter('text_size'))
        left_box.add_widget(lbl_pagamento)

        pay_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=48, spacing=10)
        btn_carta = CustomButton(text="CARTA", bg_color=(0.15, 0.45, 0.9, 1), font_size='13sp', bold=True)
        btn_carta.bind(on_press=lambda x: app_instance.completa_vendita("CARTA"))

        btn_twint = CustomButton(text="TWINT", bg_color=(0.25, 0.8, 0.95, 1), color=(0.1, 0.1, 0.1, 1), font_size='13sp', bold=True)
        btn_twint.bind(on_press=lambda x: app_instance.completa_vendita("TWINT"))

        btn_cash = CustomButton(text="CASH", bg_color=(1.0, 0.75, 0.15, 1), color=(0.1, 0.1, 0.1, 1), font_size='13sp', bold=True)
        btn_cash.bind(on_press=lambda x: app_instance.completa_vendita("CASH"))

        pay_box.add_widget(btn_carta)
        pay_box.add_widget(btn_twint)
        pay_box.add_widget(btn_cash)
        left_box.add_widget(pay_box)
        layout.add_widget(left_box)

        # --- COLONNA DI DESTRA (Reparti e Tastierino) ---
        right_box = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.48)
        app_instance.input_codice = TextInput(text="", hint_text="Input / Tastierino / Barcode", multiline=False, size_hint_y=None, height=46, font_size='16sp')
        right_box.add_widget(app_instance.input_codice)

        app_instance.lbl_stato_corrente = Label(text="Pronto: Clicca un Reparto, inserisci quantità/prezzo e conferma", size_hint_y=None, height=22, font_size='12sp', color=(0.15, 0.45, 0.8, 1), bold=True)
        right_box.add_widget(app_instance.lbl_stato_corrente)

        lbl_seq_guida = Label(text="Reparti Rapidi (Sequenza: Clicca Reparto -> Numero -> Q.tà -> Numero -> Prezzo/Conferma)", size_hint_y=None, height=18, font_size='10sp', color=(0.4, 0.4, 0.4, 1))
        right_box.add_widget(lbl_seq_guida)

        # Griglia Reparti
        reparti_grid = GridLayout(cols=4, spacing=8, size_hint_y=None, height=160)
        app_instance.grid_reparti_pos = reparti_grid

        try:
            import sqlite3
            conn = sqlite3.connect('database/negozio.db')
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS config_reparti (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT)")
            conn.commit()
            conn.close()
        except Exception:
            pass

        def popola_reparti_db():
            print('DEBUG: Esecuzione popola_reparti_db clonata da gestione centralizzata')
            reparti_grid.clear_widgets()
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
            conn.commit()
            
            cursor.execute('SELECT id, nome, attivo, standby, colore_r, colore_g, colore_b, colore_a FROM config_reparti WHERE id BETWEEN 1 AND 12 ORDER BY id ASC')
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                r_id, r_nome, r_attivo, r_standby, cr, cg, cb, ca = row
                nome_visualizzato = r_nome.strip() if hasattr(r_nome, 'strip') else str(r_nome)
                if not nome_visualizzato:
                    nome_visualizzato = f'Slot {r_id}'

                rgba = (cr, cg, cb, ca) if (cr is not None and cg is not None and cb is not None) else (0.0, 0.18, 0.55, 1.0)
                lum = (rgba[0] * 0.299 + rgba[1] * 0.587 + rgba[2] * 0.114)
                txt_color = (0, 0, 0, 1) if lum > 0.5 else (1, 1, 1, 1)

                if not r_attivo:
                    b = CustomButton(text=f"{nome_visualizzato}\n(Disatt.)", font_size='10sp')
                    b.set_color((0.25, 0.25, 0.25, 1))
                    b.color = (0.8, 0.8, 0.8, 1)
                    b.disabled = True
                elif r_standby:
                    b = CustomButton(text=f"{nome_visualizzato}\n[STANDBY]", font_size='10sp')
                    b.set_color((0.35, 0.35, 0.35, 1))
                    b.color = (0.9, 0.9, 0.9, 1)
                    b.disabled = True
                else:
                    b = CustomButton(text=str(nome_visualizzato), font_size='11sp', bold=True)
                    b.set_color(rgba)
                    b.color = txt_color
                    # Collegamento basato sull ID o sul nome coerente
                    b.bind(on_press=lambda instance, n=r_nome.strip(), rid=r_id: app_instance.seleziona_reparto(n))

                reparti_grid.add_widget(b)

        popola_reparti_db()
        app_instance.aggiorna_griglia_reparti = popola_reparti_db

        right_box.add_widget(reparti_grid)

        # --- TASTIERINO ---
        tastierino_layout = BoxLayout(orientation='horizontal', spacing=10)

        grid_tasti = GridLayout(cols=3, spacing=8, size_hint_x=0.72)
        for t in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', ',', '⌫']:
            btn = CustomButton(text=t, bg_color=(0.88, 0.88, 0.88, 1), color=(0.1, 0.1, 0.1, 1), font_size='15sp', bold=True)
            btn.bind(on_press=lambda instance, val=t: app_instance.premi_tasto(val))
            grid_tasti.add_widget(btn)
        tastierino_layout.add_widget(grid_tasti)

        col_azioni = BoxLayout(orientation='vertical', spacing=8, size_hint_x=0.28)

        btn_qta = CustomButton(text="Q.tà", bg_color=(0.95, 0.55, 0.1, 1), font_size='15sp', bold=True)
        btn_qta.bind(on_press=lambda x: app_instance.imposta_modalita("QTA"))

        btn_prezzo = CustomButton(text="Prezzo", bg_color=(0.15, 0.5, 0.9, 1), font_size='15sp', bold=True)
        btn_prezzo.bind(on_press=lambda x: app_instance.imposta_modalita("PREZZO"))

        btn_conferma = CustomButton(text="CONFERMA", bg_color=(0.1, 0.7, 0.3, 1), font_size='14sp', bold=True)
        btn_conferma.bind(on_press=lambda x: app_instance.cerca_e_aggiungi_prodotto())

        col_azioni.add_widget(btn_qta)
        col_azioni.add_widget(btn_prezzo)
        col_azioni.add_widget(btn_conferma)
        tastierino_layout.add_widget(col_azioni)

        right_box.add_widget(tastierino_layout)
        layout.add_widget(right_box)

        print('DEBUG: Fine crea_schermata_vendita, ritorno layout')
        return layout
    @staticmethod
    def crea_schermata_magazzino(app_instance):
        return InterfacciaMagazzino()
    @staticmethod
    def crea_schermata_storico(app_instance):
        return SchermataChiusura()

    def gestisci_azione_scontrino(self, instance):
        print(f"[DEBUG] Azione scontrino attivata da {instance}")

    def aggiorna_resto(self, instance, value):
        print(f"[DEBUG] aggiorna_resto chiamato con valore: {value}")
        try:
            pass
        except Exception as e:
            print(f"[ERRORE] aggiorna_resto: {e}")



    def mostra_schermata(self, nome_schermata):
        print(f"[DEBUG] Cambio schermata verso: {nome_schermata}")
        try:
            # Rimuoviamo tutti i widget tranne il menu superiore (indice 0)
            while len(self.children) > 1:
                self.remove_widget(self.children[0])
            
            if nome_schermata == "storico":
                schermata = self.crea_schermata_storico(self) if hasattr(self, "crea_schermata_storico") else Label(text="Chiusura & Storico", color=(0,0,0,1))
            elif nome_schermata == "magazzino":
                schermata = self.crea_schermata_magazzino(self) if hasattr(self, "crea_schermata_magazzino") else Label(text="Magazzino", color=(0,0,0,1))
            else:
                schermata = self.crea_schermata_vendita(self) if hasattr(self, "crea_schermata_vendita") else Label(text="Cassa / Vendita", color=(0,0,0,1))
            
            self.add_widget(schermata)
        except Exception as e:
            print(f"[ERRORE] mostra_schermata: {e}")


    def aggiorna_resto(self, instance, value):
        self.check_stato()
        try:
            importo_ricevuto = float(value.replace(',', '.')) if value else 0.0
        except ValueError:
            importo_ricevuto = 0.0

        totale_complessivo = sum(art.get('totale_riga', 0) for art in self.articoli_scontrino)
        resto = importo_ricevuto - totale_complessivo

        if hasattr(self, 'lbl_resto') and self.lbl_resto:
            if importo_ricevuto >= totale_complessivo:
                self.lbl_resto.text = f"Resto: CHF {resto:.2f}"
            else:
                self.lbl_resto.text = "Resto: Importo insufficiente"
        print(f"DEBUG: Importo ricevuto={importo_ricevuto}, Totale={totale_complessivo}, Resto={resto}")


    def check_stato(self):
        if not hasattr(self, 'reparto_corrente'):
            self.reparto_corrente = "ALIMENTARI"
        if not hasattr(self, 'buffer_input'):
            self.buffer_input = ""
        if not hasattr(self, 'quantita_corrente'):
            self.quantita_corrente = 1.0
        if not hasattr(self, 'articoli_scontrino'):
            self.articoli_scontrino = []
        if not hasattr(self, 'pagamento_completato'):
            self.pagamento_completato = False

    def premi_tasto(self, valore):
        self.check_stato()
        if self.pagamento_completato:
            self.articoli_scontrino = []
            self.pagamento_completato = False

        val_str = str(valore)
        if val_str == "C":
            self.buffer_input = ""
            self.quantita_corrente = 1.0
        elif val_str == ",":
            if "." not in self.buffer_input:
                self.buffer_input += "."
        else:
            self.buffer_input += val_str
        print(f"DEBUG tastierino: buffer_input = {self.buffer_input}")

    def aggiorna_resto(self, instance, value):
        self.check_stato()
        try:
            importo_ricevuto = float(value.replace(',', '.')) if value else 0.0
        except ValueError:
            importo_ricevuto = 0.0

        totale_complessivo = sum(art.get('totale_riga', 0) for art in self.articoli_scontrino)
        resto = importo_ricevuto - totale_complessivo

        if hasattr(self, 'lbl_resto') and self.lbl_resto:
            if importo_ricevuto >= totale_complessivo:
                self.lbl_resto.text = f"Resto: CHF {resto:.2f}"
            else:
                self.lbl_resto.text = "Resto: Importo insufficiente"
        print(f"DEBUG: Importo ricevuto={importo_ricevuto}, Totale={totale_complessivo}, Resto={resto}")


    def check_stato(self):
        if not hasattr(self, 'reparto_corrente'):
            self.reparto_corrente = "ALIMENTARI"
        if not hasattr(self, 'buffer_input'):
            self.buffer_input = ""
        if not hasattr(self, 'quantita_corrente'):
            self.quantita_corrente = 1.0
        if not hasattr(self, 'articoli_scontrino'):
            self.articoli_scontrino = []
        if not hasattr(self, 'pagamento_completato'):
            self.pagamento_completato = False

    def premi_tasto(self, valore):
        self.check_stato()
        if self.pagamento_completato:
            self.articoli_scontrino = []
            self.pagamento_completato = False

        val_str = str(valore)
        if val_str == "C":
            self.buffer_input = ""
            self.quantita_corrente = 1.0
        elif val_str == ",":
            if "." not in self.buffer_input:
                self.buffer_input += "."
        else:
            self.buffer_input += val_str
        print(f"DEBUG tastierino: buffer_input = {self.buffer_input}")

    def imposta_modalita(self, modo):
        self.check_stato()
        if modo == "QTA":
            if self.buffer_input:
                try:
                    self.quantita_corrente = float(self.buffer_input.replace(',', '.'))
                except ValueError:
                    self.quantita_corrente = 1.0
                self.buffer_input = ""
            print(f"DEBUG: Quantità impostata a {self.quantita_corrente}")
            
        elif modo == "PREZZO":
            prezzo_unitario = 0.0
            if self.buffer_input:
                try:
                    prezzo_unitario = float(self.buffer_input.replace(',', '.'))
                except ValueError:
                    prezzo_unitario = 0.0

            if prezzo_unitario > 0:
                totale_riga = self.quantita_corrente * prezzo_unitario
                articolo = {
                    "reparto": self.reparto_corrente,
                    "qta": self.quantita_corrente,
                    "prezzo": prezzo_unitario,
                    "totale_riga": totale_riga
                }
                self.articoli_scontrino.append(articolo)
                print(f"DEBUG: Articolo aggiunto -> {articolo}")
                
                self.buffer_input = ""
                self.quantita_corrente = 1.0
                self.aggiorna_griglia_scontrino()

    def cerca_e_aggiungi_prodotto(self):
        self.imposta_modalita("PREZZO")

    def aggiorna_resto(self, instance, value):
        self.check_stato()
        try:
            importo_ricevuto = float(value.replace(',', '.')) if value else 0.0
        except ValueError:
            importo_ricevuto = 0.0

        totale_complessivo = sum(art.get('totale_riga', 0) for art in self.articoli_scontrino)
        resto = importo_ricevuto - totale_complessivo

        if hasattr(self, 'lbl_resto') and self.lbl_resto:
            if importo_ricevuto >= totale_complessivo:
                self.lbl_resto.text = f"Resto: CHF {resto:.2f}"
            else:
                self.lbl_resto.text = "Resto: Importo insufficiente"
        print(f"DEBUG: Importo ricevuto={importo_ricevuto}, Totale={totale_complessivo}, Resto={resto}")


    def aggiorna_griglia_scontrino(self):
        self.check_stato()
        if hasattr(self, 'scontrino_label') and self.scontrino_label:
            if not self.articoli_scontrino:
                self.scontrino_label.text = "Scontrino Vuoto"
            else:
                linee = []
                for art in self.articoli_scontrino:
                    qta = art.get('qta', 1.0)
                    prz = art.get('prezzo', 0.0)
                    tot_riga = art.get('totale_riga', qta * prz)
                    linee.append(f"• {art['reparto']} ({qta:g} x {prz:.2f}) = {tot_riga:.2f}")
                self.scontrino_label.text = "\n".join(linee)
                
            if hasattr(self, 'lbl_totale') and self.lbl_totale:
                totale_complessivo = sum(art.get('totale_riga', 0) for art in self.articoli_scontrino)
                self.lbl_totale.text = f"TOTALE: {getattr(self, 'valuta_corrente', 'CHF')} {totale_complessivo:.2f}"


    def completa_vendita(self, metodo_pagamento):
        self.check_stato()
        print(f"DEBUG: Pagamento completato con {metodo_pagamento}. Scontrino bloccato a schermo per verifica.")
        self.pagamento_completato = True
        self.buffer_input = ""
        self.quantita_corrente = 1.0
        if hasattr(self, 'lbl_stato_corrente') and self.lbl_stato_corrente:
            self.lbl_stato_corrente.text = f"Pagamento ({metodo_pagamento}) completato. Scontrino in verifica."
