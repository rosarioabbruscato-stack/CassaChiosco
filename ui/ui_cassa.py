# -*- coding: utf-8 -*-
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
        self.moltiplicatore = 1
        self.prezzo_custom = None

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        root = BoxLayout(orientation="vertical", spacing=0)

        # Tab superiori di navigazione fissi
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
        
        # Colonna Sinistra: Scontrino e Pagamenti
        left_box = BoxLayout(orientation="vertical", spacing=10, size_hint_x=1.1)
        
        self.lbl_scontrino = Label(text="Scontrino Vuoto", color=(0.1,0.1,0.1,1), size_hint_y=0.45, halign="left", valign="top")
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

        # Colonna Destra: Reparti e Tastierino
        right_box = BoxLayout(orientation="vertical", spacing=10, size_hint_x=1.3)
        
        self.txt_input = TextInput(hint_text="Input / Tastierino / Barcode", multiline=False, size_hint_y=None, height=42)
        right_box.add_widget(self.txt_input)

        right_box.add_widget(Label(text="Reparti Dinamici (12 Slot Configurabili)", color=(0.3,0.3,0.3,1), size_hint_y=None, height=20))

        reparti_grid = GridLayout(cols=4, spacing=5, size_hint_y=None, height=140)
        colori_reparti = [
            (1, 0.5, 0, 1), (0.95, 0.85, 0, 1), (0.85, 0.15, 0.15, 1), (0.5, 0.2, 0.7, 1),
            (1, 0.45, 0, 1), (0, 0.55, 0.25, 1), (0.1, 0.35, 0.8, 1), (0.1, 0.25, 0.7, 1),
            (0.15, 0.4, 0.85, 1), (0.1, 0.3, 0.65, 1), (0.1, 0.3, 0.65, 1), (0.4, 0.4, 0.4, 1)
        ]
        for idx in range(1, 13):
            c = colori_reparti[idx-1]
            txt = f"Reparto {idx}" if idx < 12 else "Slot 12\n(Disatt.)"
            col_testo = (0,0,0,1) if idx == 2 else (1,1,1,1)
            btn = Button(text=txt, background_normal="", background_color=c, color=col_testo, bold=True)
            if idx < 12:
                btn.bind(on_press=lambda instance, v=idx: self.premi_reparto(v))
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
        btn_qta.bind(on_press=lambda x: self.imposta_funzione("QTA"))
        
        btn_prezzo = Button(text="Prezzo", background_normal="", background_color=(0.15, 0.5, 0.9, 1), bold=True)
        btn_prezzo.bind(on_press=lambda x: self.imposta_funzione("PREZZO"))
        
        btn_conferma = Button(text="CONFERMA", background_normal="", background_color=(0.1, 0.65, 0.3, 1), bold=True)
        btn_conferma.bind(on_press=lambda x: self.conferma_input())
        
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

    def premi_reparto(self, reparto_id):
        prezzo = self.prezzo_custom if self.prezzo_custom is not None else 5.00
        if self.txt_input.text.strip():
            try:
                prezzo = float(self.txt_input.text.replace(",", "."))
            except ValueError:
                pass
        
        item = {
            "nome": f"Reparto {reparto_id}",
            "prezzo": prezzo,
            "qta": self.moltiplicatore
        }
        self.carrello.append(item)
        self.moltiplicatore = 1
        self.prezzo_custom = None
        self.txt_input.text = ""
        self.aggiorna_scontrino()

    def imposta_funzione(self, tipo):
        if tipo == "QTA":
            try:
                val = int(self.txt_input.text)
                self.moltiplicatore = val if val > 0 else 1
                self.txt_input.text = ""
            except ValueError:
                pass
        elif tipo == "PREZZO":
            try:
                val = float(self.txt_input.text.replace(",", "."))
                self.prezzo_custom = val
                self.txt_input.text = ""
            except ValueError:
                pass

    def conferma_input(self):
        txt = self.txt_input.text.strip()
        if not txt:
            return
        try:
            val = float(txt.replace(",", "."))
            item = {
                "nome": "Articolo Libero",
                "prezzo": val,
                "qta": self.moltiplicatore
            }
            self.carrello.append(item)
            self.moltiplicatore = 1
            self.txt_input.text = ""
            self.aggiorna_scontrino()
        except ValueError:
            pass

    def aggiorna_scontrino(self):
        testo = ""
        self.totale = 0.0
        for item in self.carrello:
            subtot = item["prezzo"] * item["qta"]
            self.totale += subtot
            testo += f"{item['qta']}x {item['nome']} - CHF {subtot:.2f}\n"
        
        if not testo:
            testo = "Scontrino Vuoto"
        
        self.lbl_scontrino.text = testo
        self.lbl_totale.text = f"TOTALE: CHF {self.totale:.2f}"

    def elimina_ultima_riga(self, *args):
        if self.carrello:
            self.carrello.pop()
            self.aggiorna_scontrino()

    def stampa_scontrino(self, *args):
        self.carrello = []
        self.aggiorna_scontrino()
        self.lbl_resto.text = "Resto: Stampato"

    def gestisci_pagamento(self, tipo):
        try:
            importo_ricevuto = float(self.txt_importo.text.replace(",", ".")) if self.txt_importo.text.strip() else self.totale
            resto = importo_ricevuto - self.totale
            if resto >= 0:
                self.lbl_resto.text = f"Resto: CHF {resto:.2f} ({tipo})"
            else:
                self.lbl_resto.text = "Importo insufficiente!"
        except ValueError:
            self.lbl_resto.text = f"Pagato con {tipo}"
