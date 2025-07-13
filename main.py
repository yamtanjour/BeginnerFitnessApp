import json
import os
import re
import datetime
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

WORKOUTS_FILE = "workouts.json"
EXERCISES_FILE = "all_exercises.json"
PROGRESS_FILE = "progress.json"
PREMADE_FILE = "premade_workouts.json"
EXERCISE_IMAGES_DIR = "exercise_images"

def get_file_path(filename):
    app = App.get_running_app()
    # If running outside Kivy App (e.g. for testing), fallback to current dir
    if hasattr(app, 'user_data_dir'):
        return os.path.join(app.user_data_dir, filename)
    return filename

def load_workouts():
    path = get_file_path(WORKOUTS_FILE)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def save_workouts(workouts):
    path = get_file_path(WORKOUTS_FILE)
    with open(path, "w") as f:
        json.dump(workouts, f, indent=2)

def load_exercises():
    path = get_file_path(EXERCISES_FILE)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def load_progress():
    path = get_file_path(PROGRESS_FILE)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def save_progress(progress):
    path = get_file_path(PROGRESS_FILE)
    with open(path, "w") as f:
        json.dump(progress, f, indent=2)

def load_premade_workouts():
    path = get_file_path(PREMADE_FILE)
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def display_name(name):
    return name.replace("_", " ")

def get_exercise_info(ex_name):
    exercises = load_exercises()
    for ex in exercises:
        if ex.get("name") == ex_name:
            return ex
    return None

class HomeScreen(Screen):
    pass

class MyWorkoutsScreen(Screen):
    selected_workout = None

    def on_pre_enter(self):
        workouts = load_workouts()
        box = self.ids.workouts_box
        box.clear_widgets()
        for workout in workouts:
            lbl = Label(
                text=f"[u]{display_name(workout['name'])}[/u]",
                markup=True,
                color=(1,1,1,1),
                size_hint_y=None,
                height=40
            )
            def on_lbl_touch(instance, touch, name=workout["name"]):
                if instance.collide_point(*touch.pos):
                    self.open_workout(name)
            lbl.bind(on_touch_down=on_lbl_touch)
            box.add_widget(lbl)

    def open_workout(self, workout_name):
        self.selected_workout = workout_name
        self.manager.current = 'workout_detail'

class WorkoutCreationScreen(Screen):
    selected_exercises = []

    def on_pre_enter(self):
        self.selected_exercises = []
        self.ids.workout_name.text = ""
        self.ids.exercise_list_box.clear_widgets()
        self.ids.exercise_search.text = ""
        self.ids.exercise_search_results.clear_widgets()

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
                size_hint_y=None,
                height=30
            )
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
                size_hint_y=None,
                height=30
            )
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
        workouts.append({"name": workout_name, "exercises": self.selected_exercises})
        save_workouts(workouts)
        self.manager.current = 'my_workouts'

    def load_premade_into_selection(self, workout_name, exercises):
        self.ids.workout_name.text = display_name(workout_name)
        self.selected_exercises = list(exercises)
        self.refresh_exercise_list()

class PremadePopup(Popup):
    def populate_premade_workouts(self, parent_screen):
        box = self.ids.premade_workout_box
        box.clear_widgets()
        premades = load_premade_workouts()
        for premade in premades:
            name = premade.get("name", "Unnamed")
            exercises = premade.get("exercises", [])

            layout = BoxLayout(orientation='vertical', size_hint_y=None)
            layout.bind(minimum_height=layout.setter('height'))

            lbl_name = Label(
                text=f"[b][u]{display_name(name)}[/u][/b]",
                markup=True,
                color=(1,1,1,1),
                size_hint_y=None,
                height=30
            )
            layout.add_widget(lbl_name)
            for ex in exercises:
                layout.add_widget(Label(text=f"• {display_name(ex)}", font_size='12sp', color=(1,1,1,1), size_hint_y=None, height=20))

            lbl_use = Label(
                text="[u][color=00ff00]Use This Workout[/color][/u]",
                markup=True,
                size_hint_y=None,
                height=30,
                color=(1,1,1,1)
            )
            def on_use_touch(instance, touch, w=name, e=exercises):
                if instance.collide_point(*touch.pos):
                    parent_screen.load_premade_into_selection(w, e)
                    self.dismiss()
            lbl_use.bind(on_touch_down=on_use_touch)
            layout.add_widget(lbl_use)

            box.add_widget(layout)

class WorkoutDetailScreen(Screen):
    workout = None

    def on_pre_enter(self):
        workout_name = self.manager.get_screen('my_workouts').selected_workout
        workouts = load_workouts()
        for w in workouts:
            if w["name"] == workout_name:
                self.workout = w
                break
        box = self.ids.workout_detail_box
        box.clear_widgets()
        for ex in self.workout["exercises"]:
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10, padding=[5,0,5,0])
            lbl = Label(
                text=display_name(ex),
                size_hint_x=0.6,
                halign='left',
                valign='middle',
                color=(1,1,1,1),
                text_size=(None, None)
            )
            lbl.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))
            row.add_widget(lbl)
            cb = CheckBox(active=False, size_hint_x=0.15)
            row.add_widget(cb)
            info_lbl = Label(
                text='[u][color=2980b9]More Info[/color][/u]',
                markup=True,
                size_hint_x=0.25,
                valign='middle',
                halign='center',
                color=(1,1,1,1)
            )
            def on_info_touch(instance, touch, name=ex):
                if instance.collide_point(*touch.pos):
                    self.show_exercise_info(name)
            info_lbl.bind(on_touch_down=on_info_touch)
            row.add_widget(info_lbl)
            box.add_widget(row)
            box.add_widget(Widget(size_hint_y=None, height=2))

    def show_exercise_info(self, ex_name):
        ex_info = get_exercise_info(ex_name)
        if not ex_info:
            content = Label(text="No info found.", size_hint_y=None, height=40, color=(1,1,1,1))
            popup = Popup(title="Exercise Info", content=content, size_hint=(0.9, 0.7))
            popup.open()
            return

        instructions = "\n".join(ex_info.get("instructions", []))
        images = ex_info.get("images", [])[:2]

        instr_label = Label(
            text=instructions if instructions else "No instructions available.",
            color=(1,1,1,1),
            size_hint_y=None,
            halign='left',
            valign='top',
            padding_x=10
        )
        def update_text_size(instance, value):
            instance.text_size = (value, None)
            instance.texture_update()
            instance.height = instance.texture_size[1]
        instr_label.bind(width=update_text_size)
        scroll = ScrollView(size_hint_y=None, height=160)
        scroll.add_widget(instr_label)
        scroll.scroll_y = 1

        img_vbox = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None)
        for img_name in images:
            img_path = os.path.join(EXERCISE_IMAGES_DIR, img_name)
            if os.path.exists(img_path):
                img_vbox.add_widget(Image(source=img_path, size_hint=(None, None), size=(320, 220)))
            else:
                img_vbox.add_widget(Label(text="No image", size_hint=(None, None), size=(320, 220), color=(1,1,1,1)))
        img_vbox.height = len(images) * 235

        layout = BoxLayout(orientation='vertical', spacing=10, padding=[10,10,10,10])
        layout.add_widget(Label(text="Instructions:", color=(1,1,1,1), size_hint_y=None, height=30, bold=True))
        layout.add_widget(scroll)
        layout.add_widget(Label(text="Images:", color=(1,1,1,1), size_hint_y=None, height=30, bold=True))
        layout.add_widget(img_vbox)

        popup = Popup(title=display_name(ex_name), content=layout, size_hint=(0.98, 0.85))
        popup.open()

    def finish_workout(self):
        progress = load_progress()
        entry = {
            "workout": self.workout["name"],
            "exercises": list(self.workout["exercises"]),
            "timestamp": datetime.datetime.now().isoformat()
        }
        progress.append(entry)
        save_progress(progress)
        popup = Popup(title="Workout Finished", content=Label(text="Workout marked as finished!", color=(1,1,1,1)), size_hint=(0.7, 0.3))
        popup.open()

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

class ProgressScreen(Screen):
    def on_pre_enter(self):
        box = self.ids.progress_box
        box.clear_widgets()
        progress = load_progress()
        for entry in reversed(progress):
            workout = entry.get("workout", "Unknown")
            date = entry.get("timestamp", "")[:10]
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            lbl = Label(
                text=f"[u]{display_name(workout)}[/u]",
                markup=True,
                color=(1,1,1,1),
                size_hint_x=0.7
            )
            row.add_widget(lbl)
            row.add_widget(Label(text=date, color=(1,1,1,1), size_hint_x=0.3))
            box.add_widget(row)

    def go_to_stats(self):
        self.manager.current = 'stats'

class TipsScreen(Screen):
    pass

class GreenButton(Button):
    pass

class WorkItApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.2, 0.5, 1)  # blue background
        # Window.size = (360, 640)  # REMOVE THIS LINE for Android compatibility
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(MyWorkoutsScreen(name='my_workouts'))
        sm.add_widget(WorkoutCreationScreen(name='workout_creation'))
        sm.add_widget(TipsScreen(name='tips'))
        sm.add_widget(WorkoutDetailScreen(name='workout_detail'))
        sm.add_widget(ProgressScreen(name='progress'))
        sm.add_widget(StatsScreen(name='stats'))
        return sm

if __name__ == "__main__":
    WorkItApp().run()
