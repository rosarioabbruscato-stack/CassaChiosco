import os

target = "cassa-chiosco/ui/ui_cassa.py"
if not os.path.exists(target):
    target = "ui/ui_cassa.py"

code = """# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.app import App

class InterfacciaCassa(Screen):
    def __init__(self, **kwargs):
        super(InterfacciaCassa, self).__init__(**kwargs)
        
        self.carrello = []
        self.totale = 0.0
        self.item_corrente = None
        self.pagamento_completato = False

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        root = BoxLayout(orientation="vertical", spacing=0)

        top_tabs = BoxLayout(size_hint_y=None, height=45, spacing=2)
        btn_tab_cassa = Button(text="Cassa / Vendita", background_normal="", background_color=(0.15, 0.1, 0.4, 1), bold=True)
        btn_tab_mag = Button(text="Magazzino", background_normal="", background_color=(0.25, 0.25, 0.25, 1), bold=True)
        btn_tab_mag.bind(on_press=lambda x: self.vai_a_schermata("magazzino"))
        btn_tab_storico = Button(text="Chiusura & Storico", background_normal="", background_color=(0.25, 0.25, 0.25, 1), bold=True)
        btn_tab_storico.bind(on_press=lambda x: self.vai_a_schermata("chiusura"))
        
        top_tabs.add_widget(btn_tab_cassa)
        top_tabs.add_widget(btn_tab_mag)
        top_tabs.add_widget(btn_tab_storico)
        root.add_widget(top_tabs)

        main_content = BoxLayout(orientation="horizontal", padding=12, spacing=12)
        
        left_box = BoxLayout(orientation="vertical", spacing=10, size_hint_x=1.1)
        
        # Abilitato markup=True per gestire il grassetto [b]...[/b]
        self.lbl_scontrino = Label(text="Scontrino Vuoto", color=(0.1,0.1,0.1,1), size_hint_y=0.45, halign="left", valign="top", markup=True)
        self.lbl_scontrino.bind(size=self.lbl_scontrino.setter("text_size"))
        left_box.add_widget(self.lbl_scontrino)
        
        actions_box = BoxLayout(size_hint_y=None, height=45, spacing=6)
        btn_elimina = Button(text="ELIMINA RIGA", background_normal="", background_color=(0.9, 0.2, 0.2, 1), bold=True)
        btn_elimina.bind(on_press=self.elimina_ultima_riga)
        btn_stampa = Button(text="STAMPA", background_normal="", background_color=(0.9, 0.2, 0.2, 1), bold=True)
        btn_stampa.bind(on_press=self.stampa_scontrino)
        actions_box.add_widget(btn_elimina)
        actions_box.add_widget(btn_stampa)
        left_box.add_widget(actions_box)

        self.lbl_totale = Label(text="TOTALE: CHF 0.00", bold=True, font_size=20, color=(0,0,0,1), size_hint_y=None, height=40)
        left_box.add_widget(self.lbl_totale)
        
        self.lbl_resto = Label(text="Resto: -", color=(0, 0.6, 0.2, 1), bold=True, size_hint_y=None, height=25)
        left_box.add_widget(self.lbl_resto)

        pay_input_box = BoxLayout(size_hint_y=None, height=40, spacing=6)
        pay_input_box.add_widget(Label(text="Importo Ricevuto:", color=(0.1,0.1,0.1,1), size_hint_x=0.6))
        self.txt_importo = TextInput(hint_text="Contanti", multiline=False)
        pay_input_box.add_widget(self.txt_importo)
        left_box.add_widget(pay_input_box)

        left_box.add_widget(Label(text="Seleziona Pagamento:", color=(0.1,0.1,0.1,1), size_hint_y=None, height=20))
        pay_buttons = BoxLayout(size_hint_y=None, height=50, spacing=6)
        btn_carta = Button(text="CARTA", background_normal="", background_color=(0.15, 0.5, 0.9, 1), bold=True)
        btn_carta.bind(on_press=lambda x: self.gestisci_pagamento("CARTA"))
        btn_twint = Button(text="TWINT", background_normal="", background_color=(0.2, 0.75, 0.85, 1), bold=True, color=(0,0,0,1))
        btn_twint.bind(on_press=lambda x: self.gestisci_pagamento("TWINT"))
        btn_cash = Button(text="CASH", background_normal="", background_color=(1, 0.75, 0.1, 1), bold=True, color=(0,0,0,1))
        btn_cash.bind(on_press=lambda x: self.gestisci_pagamento("CASH"))
        pay_buttons.add_widget(btn_carta)
        pay_buttons.add_widget(btn_twint)
        pay_buttons.add_widget(btn_cash)
        left_box.add_widget(pay_buttons)

        main_content.add_widget(left_box)

        right_box = BoxLayout(orientation="vertical", spacing=10, size_hint_x=1.3)
        self.txt_input = TextInput(hint_text="Scrivi qui Q.tà o Prezzo", multiline=False, size_hint_y=None, height=42)
        right_box.add_widget(self.txt_input)

        self.lbl_stato_attivo = Label(text="Sequenza: 1) Reparto -> 2) Q.tà -> 3) Prezzo", color=(0.1, 0.4, 0.8, 1), bold=True, size_hint_y=None, height=22)
        right_box.add_widget(self.lbl_stato_attivo)

        right_box.add_widget(Label(text="Reparti Dinamici (12 Slot Configurabili)", color=(0.3,0.3,0.3,1), size_hint_y=None, height=20))

        reparti_grid = GridLayout(cols=4, spacing=5, size_hint_y=None, height=130)
        colori_reparti = [
            (1, 0.5, 0, 1), (0.95, 0.85, 0, 1), (0.85, 0.15, 0.15, 1), (0.5, 0.2, 0.7, 1),
            (1, 0.45, 0, 1), (0, 0.55, 0.25, 1), (0.1, 0.35, 0.8, 1), (0.1, 0.25, 0.7, 1),
            (0.15, 0.4, 0.85, 1), (0.1, 0.3, 0.65, 1), (0.1, 0.3, 0.65, 1), (0.4, 0.4, 0.4, 1)
        ]
        for idx in range(1, 13):
            c = colori_reparti[idx-1]
            txt = f"Reparto {idx}" if idx < 12 else "Slot 12\\n(Disatt.)"
            col_testo = (0,0,0,1) if idx == 2 else (1,1,1,1)
            btn = Button(text=txt, background_normal="", background_color=c, color=col_testo, bold=True)
            if idx < 12:
                btn.bind(on_press=lambda instance, v=idx: self.seleziona_reparto(v))
            reparti_grid.add_widget(btn)
        right_box.add_widget(reparti_grid)

        bottom_pad_box = BoxLayout(orientation="horizontal", spacing=6)
        numpad_grid = GridLayout(cols=3, spacing=5, size_hint_x=2.2)
        for t in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ",", "⌫"]:
            btn = Button(text=str(t), background_normal="", background_color=(0.92, 0.92, 0.92, 1), color=(0.1,0.1,0.1,1), bold=True)
            btn.bind(on_press=lambda instance, val=t: self.premi_tasto(val))
            numpad_grid.add_widget(btn)
        bottom_pad_box.add_widget(numpad_grid)

        func_grid = BoxLayout(orientation="vertical", spacing=5, size_hint_x=1)
        btn_qta = Button(text="Q.tà", background_normal="", background_color=(1, 0.55, 0.1, 1), bold=True)
        btn_qta.bind(on_press=lambda x: self.imposta_quantita())
        btn_prezzo = Button(text="Prezzo", background_normal="", background_color=(0.15, 0.5, 0.9, 1), bold=True)
        btn_prezzo.bind(on_press=lambda x: self.imposta_prezzo())
        btn_conferma = Button(text="CONFERMA", background_normal="", background_color=(0.1, 0.65, 0.3, 1), bold=True)
        btn_conferma.bind(on_press=lambda x: self.conferma_fine_ordine())
        
        func_grid.add_widget(btn_qta)
        func_grid.add_widget(btn_prezzo)
        func_grid.add_widget(btn_conferma)
        bottom_pad_box.add_widget(func_grid)

        right_box.add_widget(bottom_pad_box)
        main_content.add_widget(right_box)

        root.add_widget(main_content)
        self.add_widget(root)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def vai_a_schermata(self, nome_schermata):
        if self.manager:
            self.manager.current = nome_schermata
        else:
            app = App.get_running_app()
            if app and hasattr(app, "root") and app.root:
                app.root.current = nome_schermata

    def premi_tasto(self, val, *args):
        current = self.txt_input.text
        if val == "⌫":
            self.txt_input.text = current[:-1]
        else:
            self.txt_input.text = current + str(val)

    def seleziona_reparto(self, reparto_id):
        if self.pagamento_completato:
            self.lbl_stato_attivo.text = "Ordine completato. Premi CONFERMA per il nuovo cliente."
            return

        self.item_corrente = {
            "nome": f"Reparto {reparto_id}",
            "prezzo": 0.0,
            "qta": 1
        }
        self.carrello.append(self.item_corrente)
        self.aggiorna_scontrino()
        
        self.txt_input.text = "1"
        self.lbl_stato_attivo.text = f"Reparto {reparto_id} inserito. Ora scrivi Q.tà e premi Q.tà"

    def imposta_quantita(self):
        if self.item_corrente is None:
            self.lbl_stato_attivo.text = "ATTENZIONE: Seleziona prima un Reparto!"
            return

        txt_val = self.txt_input.text.strip()
        try:
            val = int(txt_val) if txt_val else 1
            self.item_corrente["qta"] = val if val > 0 else 1
            self.aggiorna_scontrino()
            
            self.txt_input.text = ""
            self.lbl_stato_attivo.text = f"Q.tà impostata a {self.item_corrente['qta']}. Ora scrivi il Prezzo e premi Prezzo"
        except ValueError:
            self.lbl_stato_attivo.text = "Quantità non valida"

    def imposta_prezzo(self):
        if self.item_corrente is None:
            self.lbl_stato_attivo.text = "ATTENZIONE: Seleziona prima un Reparto!"
            return

        txt_val = self.txt_input.text.strip()
        try:
            val = float(txt_val.replace(",", ".")) if txt_val else 0.0
            if val > 0:
                self.item_corrente["prezzo"] = val
                self.aggiorna_scontrino()
                
                self.lbl_stato_attivo.text = f"Registrato: {self.item_corrente['qta']}x {self.item_corrente['nome']} @ CHF {val:.2f}"
                self.item_corrente = None
                self.txt_input.text = ""
            else:
                self.lbl_stato_attivo.text = "Inserisci un prezzo maggiore di zero"
        except ValueError:
            self.lbl_stato_attivo.text = "Prezzo non valido"

    def conferma_input(self):
        pass

    def conferma_fine_ordine(self, *args):
        print("[CASSA] Ordine chiuso. Pronto per il prossimo cliente.")
        self.carrello = []
        self.totale = 0.0
        self.item_corrente = None
        self.pagamento_completato = False
        self.txt_importo.text = ""
        self.lbl_resto.text = "Resto: -"
        self.txt_input.text = ""
        self.lbl_stato_attivo.text = "Sequenza: 1) Reparto -> 2) Q.tà -> 3) Prezzo"
        self.aggiorna_scontrino()

    def aggiorna_scontrino(self):
        testo = ""
        self.totale = 0.0
        for item in self.carrello:
            subtot = item["prezzo"] * item["qta"]
            self.totale += subtot
            # Formato richiesto: REPARTO - QUANTITA x PREZZO = SUBTOTALE (subtotale in grassetto con markup)
            testo += f"{item['nome']} - {item['qta']} x CHF {item['prezzo']:.2f} = [b]CHF {subtot:.2f}[/b]\\n"
        
        if not testo:
            testo = "Scontrino Vuoto"
        
        self.lbl_scontrino.text = testo
        self.lbl_totale.text = f"TOTALE: CHF {self.totale:.2f}"

    def elimina_ultima_riga(self, *args):
        if not self.pagamento_completato and self.carrello:
            self.carrello.pop()
            self.item_corrente = None
            self.aggiorna_scontrino()

    def stampa_scontrino(self, *args):
        print("[STAMPANTE] Stampa scontrino in corso...")
        self.lbl_resto.text = "Resto: Stampato (Controlla lo scontrino)"

    def gestisci_pagamento(self, tipo):
        try:
            importo_ricevuto = float(self.txt_importo.text.replace(",", ".")) if self.txt_importo.text.strip() else self.totale
            resto = importo_ricevuto - self.totale
            if resto >= 0:
                self.lbl_resto.text = f"Resto: CHF {resto:.2f} ({tipo})"
            else:
                self.lbl_resto.text = "Importo insufficiente!"
            self.pagamento_completato = True
            print(f"[CASSA] Pagamento registrato ({tipo}). Transazione bloccata a video per il controllo del cliente.")
        except ValueError:
            self.lbl_resto.text = f"Pagato con {tipo}"
            self.pagamento_completato = True
"""

with open(target, "w", encoding="utf-8") as f:
    f.write(code)
print("File ui_cassa.py aggiornato correttamente!")
