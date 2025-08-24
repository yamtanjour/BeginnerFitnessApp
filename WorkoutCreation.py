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
from data_handling import load_workouts, load_exercises, display_name, save_workouts
from kivy.clock import Clock
from kivy.metrics import dp

class WorkoutCreationScreen(Screen):
    
    selected_exercises = []
    edit_mode = False
    editing_workout_name = None
    _all_exercises = None
    _search_event = None
    _search_bound = False

    def on_pre_enter(self):
        # load exercises once and refresh UI
        if self._all_exercises is None:
            self._all_exercises = load_exercises()
        self.refresh_exercise_list()

    def load_premade_into_selection(self, name, exercises):
        """Called by PremadeScreen: load premade into creator for editing."""
        self.edit_mode = True
        self.editing_workout_name = name
        self.selected_exercises = list(exercises or [])
        # set workout name input if present in KV (use id from workit.kv)
        try:
            if 'workout_name' in self.ids:
                self.ids.workout_name.text = name
        except Exception:
            pass
        self.refresh_exercise_list()

    def add_exercise(self, exercise_name):
        if exercise_name and exercise_name not in self.selected_exercises:
            self.selected_exercises.append(exercise_name)
            self.refresh_exercise_list()

    def remove_exercise(self, exercise_name):
        try:
            self.selected_exercises.remove(exercise_name)
        except ValueError:
            pass
        self.refresh_exercise_list()

    def refresh_exercise_list(self):
        """Refresh the visual list of selected exercises (expects id 'exercise_list_box' in KV)."""
        box = self.ids.get('exercise_list_box')
        if not box:
            return
        box.clear_widgets()
        for ex in self.selected_exercises:
            btn = Button(text=display_name(ex), size_hint_y=None, height=dp(40))
            # tap to remove (simple behavior); change to drag/reorder as needed
            btn.bind(on_release=lambda inst, e=ex: self.remove_exercise(e))
            box.add_widget(btn)