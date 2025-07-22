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
from data_handling import load_progress, display_name, load_exercises
from main import GreenButton


class StatsScreen(Screen):
    def on_pre_enter(self):
        self.populate_stats()

    def populate_stats(self):
        box = self.ids.stats_box
        box.clear_widgets()
        progress = load_progress()
        exercises_data = load_exercises()

        def make_label(text, **kwargs):
            lbl = Label(
                text=text,
                color=(1,1,1,1),
                size_hint_y=None,
                height=kwargs.get('height', 28),
                markup=kwargs.get('markup', False),
                halign='left'
            )
            lbl.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
            return lbl

        # General Stats
        total_workouts = len(progress)
        all_exercise_names = []
        workout_dates = []
        for entry in progress:
            workout_dates.append(entry.get("timestamp", "")[:10])
            all_exercise_names.extend(entry.get("exercises", []))
        total_exercises = len(all_exercise_names)
        unique_dates = set(workout_dates)
        if unique_dates:
            first_date = min(unique_dates)
            last_date = max(unique_dates)
            days = (datetime.datetime.fromisoformat(last_date) - datetime.datetime.fromisoformat(first_date)).days + 1
            avg_per_week = round(total_workouts / (days / 7), 2) if days > 0 else total_workouts
        else:
            avg_per_week = 0

        # Streak calculation
        streak = 0
        sorted_dates = sorted(unique_dates)
        if sorted_dates:
            streak = 1
            prev = datetime.datetime.fromisoformat(sorted_dates[0])
            for d in sorted_dates[1:]:
                curr = datetime.datetime.fromisoformat(d)
                if (curr - prev).days == 1:
                    streak += 1
                else:
                    streak = 1
                prev = curr

        # General Stats UI
        box.add_widget(make_label("[b]General Stats[/b]", markup=True, height=36))
        box.add_widget(make_label(f"Total Workouts: {total_workouts}"))
        box.add_widget(make_label(f"Total Exercises Performed: {total_exercises}"))
        box.add_widget(make_label(f"Average Workouts/Week: {avg_per_week}"))
        box.add_widget(make_label(f"Longest Streak: {streak} days"))
        box.add_widget(Widget(size_hint_y=None, height=10))

        # Muscle Group Distribution
        muscle_counter = Counter()
        ex_dict = {ex.get("name"): ex for ex in exercises_data}
        for ex_name in all_exercise_names:
            ex = ex_dict.get(ex_name)
            if ex:
                for m in ex.get("primaryMuscles", []):
                    muscle_counter[m] += 1
                for m in ex.get("secondaryMuscles", []):
                    muscle_counter[m] += 1
        top_muscles = muscle_counter.most_common(5)
        box.add_widget(make_label("[b]Muscle Group Distribution (Top 5)[/b]", markup=True, height=36))
        for muscle, count in top_muscles:
            box.add_widget(make_label(f"{muscle}: {count}"))
        if len(muscle_counter) > 5:
            btn = GreenButton(text="Show All Muscle Groups", size_hint_y=None, height=36)
            btn.bind(on_release=lambda instance: self.show_muscle_popup(muscle_counter))
            box.add_widget(btn)
        box.add_widget(Widget(size_hint_y=None, height=10))

        # Exercise Frequency
        freq_counter = Counter(all_exercise_names)
        top_exercises = freq_counter.most_common(5)
        box.add_widget(make_label("[b]Exercise Frequency (Top 5)[/b]", markup=True, height=36))
        for ex_name, count in top_exercises:
            box.add_widget(make_label(f"{display_name(ex_name)}: {count}"))
        if len(freq_counter) > 5:
            btn = GreenButton(text="Show All Exercises", size_hint_y=None, height=36)
            btn.bind(on_release=lambda instance: self.show_exercise_popup(freq_counter))
            box.add_widget(btn)

    def show_muscle_popup(self, muscle_counter):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        sorted_muscles = sorted(muscle_counter.items(), key=lambda x: -x[1])
        for muscle, count in sorted_muscles:
            lbl = Label(text=f"{muscle}: {count}", color=(1,1,1,1), size_hint_y=None, height=28, halign='left')
            lbl.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
            layout.add_widget(lbl)
        scroll = ScrollView(size_hint=(1,1), do_scroll_x=False, do_scroll_y=True, bar_width=8, scroll_type=['bars', 'content'])
        scroll.add_widget(layout)
        popup = Popup(title="All Muscle Groups", content=scroll, size_hint=(0.9, 0.8))
        popup.open()

    def show_exercise_popup(self, freq_counter):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=8, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        sorted_ex = sorted(freq_counter.items(), key=lambda x: -x[1])
        for ex_name, count in sorted_ex:
            lbl = Label(text=f"{display_name(ex_name)}: {count}", color=(1,1,1,1), size_hint_y=None, height=28, halign='left')
            lbl.bind(width=lambda instance, value: setattr(instance, 'text_size', (value, None)))
            layout.add_widget(lbl)
        scroll = ScrollView(size_hint=(1,1), do_scroll_x=False, do_scroll_y=True, bar_width=8, scroll_type=['bars', 'content'])
        scroll.add_widget(layout)
        popup = Popup(title="All Exercises", content=scroll, size_hint=(0.9, 0.8))
        popup.open()