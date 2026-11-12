from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

Window.clearcolor = (0.95, 0.95, 0.97, 1)

COLORI_REPARTI = {
    "ALIMENTARI": (1.0, 0.6, 0.15, 1),
    "BIBITE": (1.0, 0.8, 0.2, 1),
    "CUCINA": (0.7, 0.85, 0.2, 1),
    "LOTTO": (0.6, 0.35, 0.85, 1),
    "LOTTO VINCITE": (0.25, 0.65, 0.95, 1),
    "NON ALIMENTARI": (0.95, 0.3, 0.55, 1),
    "SIGARETTE": (0.2, 0.75, 0.65, 1)
}

class CustomButton(Button):
    def __init__(self, bg_color=(0.2, 0.2, 0.2, 1), **kwargs):
        super().__init__(**kwargs)
        self.bg_color = bg_color
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        
        with self.canvas.before:
            self.col_inst = Color(*self.bg_color)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def set_color(self, rgba):
        self.bg_color = rgba
        self.col_inst.rgba = rgba
