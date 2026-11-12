class ThermalPrinter:
    def __init__(self, porta=None):
        self.porta = porta

    def stampa_scontrino(self, dati_carrello):
        """Invia i dati al driver della stampante termica."""
        print("--- SIMULAZIONE STAMPA SCONTRINO ---")
        total = 0
        for articolo in dati_carrello:
            print(f"{articolo['nome']} - {articolo['prezzo']} EUR")
            total += articolo['prezzo']
        print(f"TOTALE: {total} EUR")
        print("-----------------------------------")
        return True
