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
