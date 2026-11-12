from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp

# Importiamo i nostri blocchi stagni isolati
from core.config import DB_PATH
from database.db_manager import DatabaseManager
from hardware.printer import ThermalPrinter
from ui.ui_cassa import InterfacciaCassa

class PosRootLayout(InterfacciaCassa):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Svuotiamo eventuali widget creati automaticamente dal vecchio init
        self.clear_widgets()

        # Variabili di stato globali dell'applicazione
        self.db_name = DB_PATH
        self.valuta_corrente = "CHF"
        self.articoli_scontrino = []
        self.quantita_corrente = 1.0
        self.buffer_input = ""
        self.reparto_corrente = "ALIMENTARI"
        self.pagamento_completato = False

        # Inizializziamo i componenti hardware e database isolati
        self.db = DatabaseManager()
        self.printer = ThermalPrinter()

        # 1. BLOCCO FISSO IN ALTO: Il Menu di Navigazione non si muove mai
        self.menu_bar = self.crea_menu_superiore(self)
        self.add_widget(self.menu_bar)

        # 2. CONTENITORE CENTRALE DINAMICO: Qui cambiano le schermate (Cassa, Magazzino, Storico)
        self.area_contenuto = BoxLayout(orientation='vertical')
        self.add_widget(self.area_contenuto)

        # Mostriamo subito la schermata di vendita iniziale
        self.mostra_schermata("vendita")

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

    def seleziona_reparto(self, nome_reparto):
        self.reparto_corrente = nome_reparto
        if hasattr(self, "lbl_stato_corrente") and self.lbl_stato_corrente:
            self.lbl_stato_corrente.text = f"Reparto: {nome_reparto}. Inserisci Q.tà o Prezzo."

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
        elif val_str == "⌫":
            self.buffer_input = self.buffer_input[:-1]
        else:
            self.buffer_input += val_str
            
        if hasattr(self, 'input_codice') and self.input_codice:
            self.input_codice.text = self.buffer_input

    def imposta_modalita(self, modo):
        self.check_stato()
        if modo == "QTA":
            if self.buffer_input:
                try:
                    self.quantita_corrente = float(self.buffer_input.replace(',', '.'))
                except ValueError:
                    self.quantita_corrente = 1.0
                self.buffer_input = ""
                if hasattr(self, 'input_codice'):
                    self.input_codice.text = ""
            print(f"[DEBUG] Quantità impostata a {self.quantita_corrente}")

    def cerca_e_aggiungi_prodotto(self):
        self.check_stato()
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
            self.buffer_input = ""
            self.quantita_corrente = 1.0
            if hasattr(self, 'input_codice'):
                self.input_codice.text = ""
            self.aggiorna_griglia_scontrino()

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
                    linee.append(f"• {art['reparto']} ({qta:g} x {prz:.2f}) = [b]{tot_riga:.2f}[/b]")
                self.scontrino_label.text = "\n".join(linee)

        if hasattr(self, 'lbl_totale') and self.lbl_totale:
            totale_complessivo = sum(art.get('totale_riga', 0) for art in self.articoli_scontrino)
            self.lbl_totale.text = f"TOTALE: {getattr(self, 'valuta_corrente', 'CHF')} {totale_complessivo:.2f}"

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

    def gestisci_azione_scontrino(self, instance):
        if self.articoli_scontrino:
            rimosso = self.articoli_scontrino.pop()
            print(f"[OK] Rimosso articolo: {rimosso}")
            self.aggiorna_griglia_scontrino()

    def completa_vendita(self, metodo_pagamento):
        self.check_stato()
        print(f"[OK] Vendita completata con {metodo_pagamento}.")
        self.pagamento_completato = True
        self.buffer_input = ""
        self.quantita_corrente = 1.0
        if hasattr(self, 'lbl_stato_corrente') and self.lbl_stato_corrente:
            self.lbl_stato_corrente.text = f"Pagamento ({metodo_pagamento}) completato."

    def stampa_scontrino_manuale(self, instance):
        if not self.articoli_scontrino:
            print("[INFO] Scontrino vuoto.")
            return
        self.printer.stampa_scontrino(self.articoli_scontrino)

    def esegui_chiusura_z(self, instance):
        print("[OK] Chiusura Z registrata.")

    def mostra_schermata(self, nome_schermata):
        """Aggiorna solo l'area centrale mantenendo il menu superiore fisso."""
        try:
            self.area_contenuto.clear_widgets()

            if nome_schermata == "storico":
                schermata = self.crea_schermata_storico(self)
            elif nome_schermata == "magazzino":
                schermata = self.crea_schermata_magazzino(self)
            else:
                schermata = self.crea_schermata_vendita(self)

            self.area_contenuto.add_widget(schermata)
        except Exception as e:
            print(f"[ERRORE] mostra_schermata: {e}")

class MainApp(App):
    def build(self):
        self.title = "CassaChiosco - POS Modulare Blindato"
        return PosRootLayout()

    def on_start(self):
        from kivy.core.window import Window
        Window.size = (1024, 768)
        Window.show()
        print("[OK] Finestra forzata alla visualizzazione.")

if __name__ == '__main__':
    MainApp().run()
