import os
import platform
import socket

def genera_scontrino_formattato(testo_base):
    INIT = b'\x1b\x40'
    CUT_PAPER = b'\x1d\x56\x41\x03'
    
    scontrino_bytes = INIT
    scontrino_bytes += testo_base.encode('utf-8', errors='ignore')
    scontrino_bytes += b'\n\n\n'
    scontrino_bytes += CUT_PAPER
    
    return scontrino_bytes

def stampa_scontrino_rawbt(testo_scontrino):
    dati_bytes = genera_scontrino_formattato(testo_scontrino)
    
    if platform.platform().lower().find('android') >= 0:
        try:
            # Import locale sicuro per evitare crash all'avvio dell'app
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            
            activity = PythonActivity.mActivity
            if activity is not None:
                file_path = os.path.join(activity.getFilesDir().getAbsolutePath(), "scontrino.bin")
                with open(file_path, "wb") as f:
                    f.write(dati_bytes)
                    
                intent = Intent(Intent.ACTION_VIEW)
                intent.setDataAndType(Uri.parse("file://" + file_path), "application/octet-stream")
                intent.setPackage("ru.a402d.rawbtprinter")
                
                activity.startActivity(intent)
                return True
        except Exception as e:
            print(f"Errore invio a RawBT su Android: {e}")
            return False
    else:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(('127.0.0.1', 9100))
            s.sendall(dati_bytes)
            s.close()
            print("Scontrino formattato inviato via socket.")
            return True
        except Exception:
            print("=== STAMPA SCONTRINO (SIMULAZIONE TERMINALE) ===")
            print(testo_scontrino)
            print("[COMANDO ESC/POS: TAGLIO CARTA ESEGUITO]")
            print("================================================")
            return True
