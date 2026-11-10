
from kivy.uix.widget import Widget
from kivy.graphics import Color, Triangle
from kivy.core.window import Window

class CursorePermanente(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            # Bordo bianco esterno per contrasto
            Color(1, 1, 1, 1)
            self.bordo = Triangle(points=[0, 0, 0, 0, 0, 0])
            # Freccia nera interna
            Color(0, 0, 0, 1)
            self.freccia = Triangle(points=[0, 0, 0, 0, 0, 0])
        Window.bind(mouse_pos=self.aggiorna_posizione)

    def aggiorna_posizione(self, window, pos):
        x, y = pos
        # Disegna una freccia stile puntatore del mouse con la punta esatta sulle coordinate (x, y)
        self.bordo.points = [x, y,  x, y - 22,  x + 15, y - 13]
        self.freccia.points = [x, y - 2,  x + 2, y - 19,  x + 12, y - 14]

def _init_cursore_custom(*args):
    try:
        from kivy.base import EventLoop
        if EventLoop.window and not any(isinstance(w, CursorePermanente) for w in EventLoop.window.children):
            cursor_widget = CursorePermanente()
            EventLoop.window.add_widget(cursor_widget)
    except Exception:
        pass

from kivy.clock import Clock
Clock.schedule_once(_init_cursore_custom, 1)


from kivy.uix.label import Label
from kivy.core.window import Window

Clock.schedule_once(_init_cursore_custom, 1)


from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window

def _init_cursore_custom(*args):
    try:
        from kivy.base import EventLoop
        if EventLoop.window and not any(isinstance(w, CursorePermanente) for w in EventLoop.window.children):
            cursor_widget = CursorePermanente()
            EventLoop.window.add_widget(cursor_widget)
    except Exception:
        pass

from kivy.clock import Clock
Clock.schedule_once(_init_cursore_custom, 1)


from kivy.config import Config
from kivy.core.window import Window
from kivy.clock import Clock

# Forzatura iniziale assoluta
Config.set('modules', 'cursor', '')
Config.set('graphics', 'show_cursor', '1')

def _blocca_e_forza_cursore(dt):
    try:
        if not Window.show_cursor:
            Window.show_cursor = True
    except Exception:
        pass

# Avviamo il controllo costante ogni 0.5 secondi per blindare il cursore
Clock.schedule_interval(_blocca_e_forza_cursore, 0.5)


from kivy.config import Config
Config.set('modules', 'cursor', '')

import sys
import os

from kivy.core.window import Window
Window.show_cursor = True

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'cassa-chiosco')))

from kivy.app import App
from ui.ui_cassa import InterfacciaCassa

class CassaApp(App):
    def build(self):
        return InterfacciaCassa()

if __name__ == '__main__':
    CassaApp().run()
