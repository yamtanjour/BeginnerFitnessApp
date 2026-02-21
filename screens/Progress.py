import json
import os
import re
import datetime
import shutil
from collections import Counter, defaultdict
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from data.data_handling import load_progress, display_name

class ProgressScreen(Screen):
    def on_pre_enter(self):
        from kivy.metrics import dp
        box = self.ids.progress_box
        box.clear_widgets()
        progress = load_progress()
        for entry in reversed(progress):
            workout = entry.get("workout", "Unknown")
            date = entry.get("timestamp", "")[:10]
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
            lbl = Label(
                text=f"[u]{display_name(workout)}[/u]",
                markup=True,
                color=(1,1,1,1),
                size_hint_x=0.7,
                font_size=dp(20)
            )
            row.add_widget(lbl)
            row.add_widget(Label(text=date, color=(1,1,1,1), size_hint_x=0.3, font_size=dp(18)))
            box.add_widget(row)

    def go_to_stats(self):
        self.manager.current = 'stats'