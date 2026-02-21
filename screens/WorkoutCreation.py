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
from data.data_handling import load_workouts, load_exercises, display_name, save_workouts
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
        # Reset edit mode when entering normally (not when called by load_premade_into_selection)
        if not getattr(self, '_loading_premade', False):
            self.edit_mode = False
            self.editing_workout_name = None
        
        # load exercises once and refresh UI
        if self._all_exercises is None:
            self._all_exercises = load_exercises()
            # normalize into list and build quick lookup
            if isinstance(self._all_exercises, dict):
                # older format: dict of key->info
                self._exercise_list = list(self._all_exercises.keys())
                self._ex_by_key = self._all_exercises
            else:
                # expected: list of exercise dicts with 'name'
                self._exercise_list = [ex.get('name') for ex in (self._all_exercises or []) if ex.get('name')]
                self._ex_by_key = {ex.get('name'): ex for ex in (self._all_exercises or []) if ex.get('name')}
        self.refresh_exercise_list()

    def load_premade_into_selection(self, name, exercises):
        """Called by PremadeScreen: load premade into creator for editing."""
        self._loading_premade = True
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
        self._loading_premade = False

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

    def find_exercise_key(self, text):
        """Try to resolve a user-typed string to a canonical exercise key from _all_exercises."""
        if not text:
            return None
        if self._all_exercises is None:
            self._all_exercises = load_exercises() or {}
        t = text.strip().lower()
        # direct key match
        if hasattr(self, '_exercise_list') and t in [k.lower() for k in self._exercise_list]:
            # return the exact key from list (case-insensitive)
            for k in self._exercise_list:
                if k.lower() == t:
                    return k
        # exact display name match
        for k in (getattr(self, '_exercise_list', []) or []):
            try:
                if display_name(k).lower() == t:
                    return k
            except Exception:
                pass
        # substring match (first match)
        for k in (getattr(self, '_exercise_list', []) or []):
            try:
                dn = display_name(k).lower()
                if t in dn or t in k.lower():
                    return k
            except Exception:
                pass
        return None

    def add_exercise_from_input(self, text):
        """Called from the TextInput on Enter: resolve and add an exercise."""
        key = self.find_exercise_key(text)
        if key:
            self.add_exercise(key)
        else:
            # fallback: add raw name (normalize spaces -> underscores)
            normalized = text.strip().replace(" ", "_")
            if normalized:
                self.add_exercise(normalized)

    def update_search_results(self, text):
        """Populate the exercise_search_results GridLayout with matching exercise buttons."""
        box = self.ids.get('exercise_search_results')
        if box is None:
            return
        box.clear_widgets()
        q = (text or '').strip().lower()
        if not q:
            return
        # ensure exercises loaded
        if self._all_exercises is None:
            self._all_exercises = load_exercises() or {}
        matches = []
        # collect matches by display name or key from normalized exercise list
        for k in (getattr(self, '_exercise_list', []) or []):
            try:
                dn = display_name(k).lower()
            except Exception:
                dn = (k or '').lower()
            if q in dn or q in (k or '').lower():
                matches.append((k, dn))
            if len(matches) >= 12:
                break
        # add a button for each match
        for key, dn in matches:
            btn = Button(text=display_name(key), size_hint_y=None, height=dp(36))
            # capture key in default arg
            def on_pick(inst, k=key):
                self.add_exercise(k)
                # clear search input and results
                try:
                    self.ids.exercise_search.text = ''
                except Exception:
                    pass
                box.clear_widgets()
            btn.bind(on_release=on_pick)
            box.add_widget(btn)

    def save_workout(self):
        """Save the current workout to the workouts file."""
        try:
            # Get workout name from the TextInput
            workout_name = self.ids.workout_name.text.strip()
            if not workout_name:
                # Show error popup if no name
                popup = Popup(title="Error", content=Label(text="Please enter a workout name."), size_hint=(0.8, 0.4))
                popup.open()
                return
            
            if not self.selected_exercises:
                # Show error popup if no exercises
                popup = Popup(title="Error", content=Label(text="Please add at least one exercise."), size_hint=(0.8, 0.4))
                popup.open()
                return
            
            # Load existing workouts
            workouts = load_workouts() or []
            
            if self.edit_mode and self.editing_workout_name:
                # Update existing workout
                workout_updated = False
                for workout in workouts:
                    if workout.get("name") == self.editing_workout_name:
                        workout["name"] = workout_name
                        workout["exercises"] = list(self.selected_exercises)
                        workout_updated = True
                        break
                
                if not workout_updated:
                    # Fall through to create new workout logic
                    if any(w.get("name") == workout_name for w in workouts):
                        popup = Popup(title="Error", content=Label(text="Workout name already exists."), size_hint=(0.8, 0.4))
                        popup.open()
                        return
                    
                    # Create new workout
                    new_workout = {
                        "name": workout_name,
                        "exercises": list(self.selected_exercises)
                    }
                    workouts.append(new_workout)
            else:
                # Check if workout name already exists
                if any(w.get("name") == workout_name for w in workouts):
                    popup = Popup(title="Error", content=Label(text="Workout name already exists."), size_hint=(0.8, 0.4))
                    popup.open()
                    return
                
                # Create new workout
                new_workout = {
                    "name": workout_name,
                    "exercises": list(self.selected_exercises)
                }
                workouts.append(new_workout)
            
            # Save workouts
            save_workouts(workouts)
            
            # Reset state
            self.selected_exercises = []
            self.edit_mode = False
            self.editing_workout_name = None
            
            # Clear the workout name input
            try:
                self.ids.workout_name.text = ""
            except:
                pass
            
            # Navigate back to my workouts
            self.manager.current = 'my_workouts'
            
        except Exception as e:
            # Show error popup
            popup = Popup(title="Error", content=Label(text=f"Failed to save workout: {str(e)}"), size_hint=(0.8, 0.4))
            popup.open()