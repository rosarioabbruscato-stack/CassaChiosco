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


class InterfacciaCassa:
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
        layout = BoxLayout(orientation='horizontal', padding=0, spacing=20)
        
        # --- COLONNA DI SINISTRA ---
        left_box = BoxLayout(orientation='vertical', padding=15, spacing=10, size_hint_x=0.50)
        
        scroll_scontrino = ScrollView()
        app_instance.scontrino_label = Label(text="Scontrino Vuoto", font_name="DejaVuSansMono" if "RobotoMono" in ["RobotoMono"] else "Courier", font_size='13sp', halign='left', valign='top', size_hint_y=None, color=(0.2, 0.2, 0.2, 1))
        app_instance.scontrino_label.bind(width=lambda *x: setattr(app_instance.scontrino_label, 'text_size', (app_instance.scontrino_label.width, None)))
        app_instance.scontrino_label.bind(texture_size=lambda *x: setattr(app_instance.scontrino_label, 'height', app_instance.scontrino_label.texture_size[1]))
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
        # Colleghiamo a un metodo di stampa manuale o generica se presente, o gestisci_azione_scontrino
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
        
        # --- COLONNA DI DESTRA (Reparti con font ridotto a 11sp) ---
        right_box = BoxLayout(orientation='vertical', spacing=10, size_hint_x=0.50)
        app_instance.input_codice = TextInput(text="", hint_text="Input / Tastierino / Barcode", multiline=False, size_hint_y=None, height=46, font_size='16sp')
        right_box.add_widget(app_instance.input_codice)
        
        app_instance.lbl_stato_corrente = Label(text="Pronto: Clicca un Reparto, inserisci quantità/prezzo e conferma", size_hint_y=None, height=22, font_size='12sp', color=(0.15, 0.45, 0.8, 1), bold=True)
        right_box.add_widget(app_instance.lbl_stato_corrente)
        
        lbl_seq_guida = Label(text="Reparti Rapidi (Sequenza: Clicca Reparto -> Numero -> Q.tà -> Numero -> Prezzo/Conferma)", size_hint_y=None, height=18, font_size='10sp', color=(0.4, 0.4, 0.4, 1))
        right_box.add_widget(lbl_seq_guida)
        
        # Griglia 12 Slot Fissi Reparti da Database (Palette Pantone)
        reparti_grid = GridLayout(cols=4, spacing=8, size_hint_y=None, height=160)
        app_instance.grid_reparti_pos = reparti_grid

        def popola_reparti_db():
            reparti_grid.clear_widgets()
            import sqlite3
            conn = sqlite3.connect('database/negozio.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, nome, attivo, standby, colore_r, colore_g, colore_b, colore_a FROM config_reparti WHERE id BETWEEN 1 AND 12 ORDER BY id ASC')
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                r_id, r_nome, r_attivo, r_standby, cr, cg, cb, ca = row
                nome_visualizzato = r_nome.rip() if hasattr(r_nome, 'rip') else (r_nome.strip() if r_nome and r_nome.strip() else f'Slot {r_id}')
                
                if not r_attivo:
                    b = CustomButton(text=f"{nome_visualizzato} (Disatt.)", bg_color=(0.25, 0.25, 0.25, 0.5), color=(0.7, 0.7, 0.7, 1), bold=False, font_size='10sp')
                    b.disabled = True
                elif r_standby:
                    b = CustomButton(text=f"{nome_visualizzato} [STANDBY]", bg_color=(0.4, 0.4, 0.4, 1), color=(0.9, 0.9, 0.9, 1), bold=True, font_size='10sp')
                    b.disabled = True
                else:
                    b = CustomButton(text=str(nome_visualizzato), bg_color=(cr, cg, cb, ca), color=(1, 1, 1, 1), bold=True, font_size='11sp')
                    b.bind(on_press=lambda instance, r_nome=nome_visualizzato: app_instance.seleziona_reparto(r_nome))

                reparti_grid.add_widget(b)

        popola_reparti_db()
        app_instance.aggiorna_griglia_reparti_pos = popola_reparti_db

        right_box.add_widget(reparti_grid)
        
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
        return layout

    @staticmethod
    def crea_schermata_magazzino(app_instance):
        return InterfacciaMagazzino()
    @staticmethod
    def crea_schermata_storico(app_instance):
        return SchermataChiusura()
