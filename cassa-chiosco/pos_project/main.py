from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from database.db_manager import DatabaseManager
from hardware.printer import ThermalPrinter

class PosRootLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs, orientation='vertical')
        
        self.db = DatabaseManager()
        self.printer = ThermalPrinter()

        self.add_widget(Label(text="Sistema POS - Architettura a Blocchi Attiva", font_size=20))
        
        btn_test = Button(text="Esegui Test Stampa Carrello", size_hint=(1, 0.2))
        btn_test.bind(on_press=self.fai_test_stampa)
        self.add_widget(btn_test)

    def fai_test_stampa(self, instance):
        carrello_prova = [
            {"nome": "Prodotto A", "prezzo": 2.50},
            {"nome": "Prodotto B", "prezzo": 5.00}
        ]
        self.printer.stampa_scontrino(carrello_prova)

class MainApp(App):
    def build(self):
        self.title = "POS Modulare Blindato"
        return PosRootLayout()

if __name__ == '__main__':
    MainApp().run()
