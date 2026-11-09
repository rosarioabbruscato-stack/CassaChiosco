from kivy.config import Config
Config.set('postproc', 'fps', '0')
Config.set('graphics', 'multisamples', '0')
# Disattiva i cerchi rossi del touch/mouse
Config.set('input', 'mouse', 'mouse,disable_multitouch=1')
from kivy.app import App
from kivy.core.window import Window
from ui.ui_cassa import InterfacciaCassa

class CassaChioscoApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        return InterfacciaCassa()

if __name__ == "__main__":
    CassaChioscoApp().run()
