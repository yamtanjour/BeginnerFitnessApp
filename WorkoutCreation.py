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
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from data_handling import load_workouts, load_exercises, display_name,display_name, save_workouts
from PremadePopup import PremadePopup

class WorkoutCreationScreen(Screen):
    
    selected_exercises = []
    edit_mode = False
    editing_workout_name = None

    def on_pre_enter(self):
        self.selected_exercises = []
        self.ids.workout_name.text = ""
        self.ids.exercise_list_box.clear_widgets()
        self.ids.exercise_search.text = ""
        self.ids.exercise_search_results.clear_widgets()
        if not self.edit_mode:
            self.editing_workout_name = None

    def open_premade_popup(self):
        popup = PremadePopup()
        popup.populate_premade_workouts(self)
        popup.open()

    def add_exercise(self, exercise_name):
        if exercise_name and exercise_name not in self.selected_exercises:
            self.selected_exercises.append(exercise_name)
            self.refresh_exercise_list()

    def refresh_exercise_list(self):
        box = self.ids.exercise_list_box
        box.clear_widgets()
        for ex in self.selected_exercises:
            lbl = Label(
                text=f"[u]{display_name(ex)}[/u]",
                markup=True,
                color=(1,1,1,1),
                font_size=20,
                size_hint_y=None,
                height=30,
                halign='center',
                valign='middle'
            )
            lbl.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))
            box.add_widget(lbl)

    def normalize(self, text):
        return re.sub(r'[\W_]+', ' ', text.lower())

    def search_exercises(self):
        query = self.normalize(self.ids.exercise_search.text.strip())
        results_box = self.ids.exercise_search_results
        results_box.clear_widgets()
        exercises = load_exercises()
        matches = []
        query_words = query.split()
        for ex in exercises:
            ex_name_norm = self.normalize(ex.get("name", ""))
            if all(word in ex_name_norm for word in query_words):
                matches.append(ex)
        for ex in matches[:10]:
            lbl = Label(
                text=f"[u]{display_name(ex['name'])}[/u]",
                markup=True,
                color=(1,1,1,1),
                font_size=20,
                size_hint_y=None,
                height=38,
                halign='center',
                valign='middle'
            )
            lbl.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))
            def on_lbl_touch(instance, touch, name=ex["name"]):
                if instance.collide_point(*touch.pos):
                    self.add_exercise(name)
            lbl.bind(on_touch_down=on_lbl_touch)
            results_box.add_widget(lbl)

    def save_workout(self):
        workout_name = self.ids.workout_name.text.strip()
        if not workout_name or not self.selected_exercises:
            return
        workouts = load_workouts()
        if getattr(self, 'edit_mode', False) and getattr(self, 'editing_workout_name', None):
            for w in workouts:
                if w['name'] == self.editing_workout_name:
                    w['name'] = workout_name
                    w['exercises'] = self.selected_exercises
                    break
            self.edit_mode = False
            self.editing_workout_name = None
        else:
            workouts.append({"name": workout_name, "exercises": self.selected_exercises})
        save_workouts(workouts)
        self.manager.current = 'my_workouts'

    def load_premade_into_selection(self, workout_name, exercises):
        self.ids.workout_name.text = display_name(workout_name)
        self.selected_exercises = list(exercises)
        self.refresh_exercise_list()