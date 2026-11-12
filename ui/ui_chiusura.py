# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.app import App

class InterfacciaChiusura(Screen):
    def __init__(self, **kwargs):
        super(InterfacciaChiusura, self).__init__(**kwargs)
        
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        root = BoxLayout(orientation="vertical", spacing=0)

        # Tab superiori di navigazione fissi
        top_tabs = BoxLayout(size_hint_y=None, height=45, spacing=2)
        btn_tab_cassa = Button(text="Cassa / Vendita", background_normal="", background_color=(0.25, 0.25, 0.25, 1), bold=True)
        btn_tab_cassa.bind(on_press=lambda x: self.vai_a("cassa"))
        
        btn_tab_mag = Button(text="Magazzino", background_normal="", background_color=(0.25, 0.25, 0.25, 1), bold=True)
        btn_tab_mag.bind(on_press=lambda x: self.vai_a("magazzino"))
        
        btn_tab_storico = Button(text="Chiusura & Storico", background_normal="", background_color=(0.15, 0.1, 0.4, 1), bold=True)
        
        top_tabs.add_widget(btn_tab_cassa)
        top_tabs.add_widget(btn_tab_mag)
        top_tabs.add_widget(btn_tab_storico)
        root.add_widget(top_tabs)

        # Contenuto Chiusura & Storico
        content = BoxLayout(orientation="vertical", padding=20, spacing=10)
        content.add_widget(Label(text="Chiusura Cassa & Storico Vendite", font_size=24, color=(0.1,0.1,0.1,1), bold=True, size_hint_y=None, height=50))
        content.add_widget(Label(text="Qui potrai visualizzare lo storico degli scontrini emessi e stampare la chiusura giornaliera.", color=(0.3,0.3,0.3,1)))
        
        root.add_widget(content)
        self.add_widget(root)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def vai_a(self, nome):
        app = App.get_running_app()
        if hasattr(app, "sm") and app.sm:
            app.sm.current = nome
        elif self.manager:
            self.manager.current = nome
