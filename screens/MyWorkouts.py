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
from kivy.metrics import dp
from data.data_handling import load_workouts, display_name, save_workouts

class MyWorkoutsScreen(Screen):
    selected_workout = None

    def on_pre_enter(self):
        workouts = load_workouts()
        box = self.ids.workouts_box
        box.clear_widgets()
        for workout in workouts:
            row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(40),
                spacing=dp(8)
            )
            lbl = Label(
                text=f"[u]{display_name(workout['name'])}[/u]",
                markup=True,
                font_size=dp(32),
                color=(1,1,1,1),
                size_hint_x=0.6,
                size_hint_y=None,
                height=dp(25)
            )
            def on_lbl_touch(instance, touch, name=workout["name"]):
                if instance.collide_point(*touch.pos):
                    self.open_workout(name)
            lbl.bind(on_touch_down=on_lbl_touch)
            row.add_widget(lbl)

            del_btn = Button(
                text="Delete",
                size_hint_x=0.10,
                size_hint_y=None,
                height=dp(30)
            )
            del_btn.background_color = (0.9,0.2,0.2,1)
            del_btn.color = (1,1,1,1)
            del_btn.font_size = dp(18)
            del_btn.bind(on_release=lambda inst, name=workout["name"]: self.delete_workout(name))
            row.add_widget(del_btn)

            box.add_widget(row)

    def open_workout(self, workout_name):
        self.selected_workout = workout_name
        self.manager.current = 'workout_detail'


    def delete_workout(self, workout_name):
        def do_delete(instance):
            workouts = load_workouts()
            workouts = [w for w in workouts if w["name"] != workout_name]
            save_workouts(workouts)
            self.on_pre_enter()
            popup.dismiss()
        layout = BoxLayout(
            orientation='vertical',
            spacing=dp(14),
            padding=[dp(14), dp(14), dp(14), dp(14)]
        )
        layout.add_widget(Label(
            text=f"Delete [b]{display_name(workout_name)}[/b]?",
            markup=True,
            color=(1,1,1,1)
        ))
        btns = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(44),
            spacing=dp(12)
        )
        btns.add_widget(Button(text="Cancel", on_release=lambda i: popup.dismiss()))
        btns.add_widget(Button(
            text="Delete",
            background_color=(0.9,0.2,0.2,1),
            color=(1,1,1,1),
            on_release=do_delete
        ))
        layout.add_widget(btns)
        popup = Popup(title="Delete Workout", content=layout, size_hint=(.75, .32))
        popup.open()