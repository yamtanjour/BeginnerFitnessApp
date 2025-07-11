import json
import os
import re
import datetime
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
EXERCISE_IMAGES_DIR = "exercise_images"

def load_workouts():
    if not os.path.exists(WORKOUTS_FILE):
        return []
    with open(WORKOUTS_FILE, "r") as f:
        return json.load(f)

def save_workouts(workouts):
    with open(WORKOUTS_FILE, "w") as f:
        json.dump(workouts, f, indent=2)

def load_exercises():
    if not os.path.exists(EXERCISES_FILE):
        return []
    with open(EXERCISES_FILE, "r") as f:
        return json.load(f)

def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return []
    with open(PROGRESS_FILE, "r") as f:
        return json.load(f)

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)

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
            btn = Button(
                text=display_name(workout["name"]),
                size_hint_y=None,
                height=40,
                on_release=lambda btn, name=workout["name"]: self.open_workout(name)
            )
            box.add_widget(btn)

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

    def add_exercise(self, exercise_name):
        if exercise_name and exercise_name not in self.selected_exercises:
            self.selected_exercises.append(exercise_name)
            self.refresh_exercise_list()

    def refresh_exercise_list(self):
        box = self.ids.exercise_list_box
        box.clear_widgets()
        for ex in self.selected_exercises:
            box.add_widget(Button(text=display_name(ex), size_hint_y=None, height=30))

    def normalize(self, text):
        # Lowercase and replace non-word characters with spaces
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
        for ex in matches[:10]:  # Show up to 10 results
            btn = Button(
                text=display_name(ex["name"]),
                size_hint_y=None,
                height=30,
                on_release=lambda btn, name=ex["name"]: self.add_exercise(name)
            )
            results_box.add_widget(btn)

    def save_workout(self):
        workout_name = self.ids.workout_name.text.strip()
        if not workout_name or not self.selected_exercises:
            return
        workouts = load_workouts()
        workouts.append({"name": workout_name, "exercises": self.selected_exercises})
        save_workouts(workouts)
        self.manager.current = 'my_workouts'

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
                color=(0,0,0,1),
                text_size=(None, None)
            )
            lbl.bind(size=lambda instance, value: setattr(instance, 'text_size', (instance.width, None)))
            row.add_widget(lbl)
            cb = CheckBox(active=False, size_hint_x=0.15)
            row.add_widget(cb)
            info_btn = Button(
                text="More Info",
                size_hint_x=0.25,
                height=40,
                on_release=lambda btn, name=ex: self.show_exercise_info(name)
            )
            row.add_widget(info_btn)
            box.add_widget(row)
            sep = Widget(size_hint_y=None, height=2)
            box.add_widget(sep)

    def show_exercise_info(self, ex_name):
        ex_info = get_exercise_info(ex_name)
        if not ex_info:
            content = Label(text="No info found.", size_hint_y=None, height=40)
            popup = Popup(title="Exercise Info", content=content, size_hint=(0.9, 0.7))
            popup.open()
            return

        instructions = "\n".join(ex_info.get("instructions", []))
        images = ex_info.get("images", [])[:2]

        # Instructions at the very top, scrollable, left-aligned, no extra space
        instr_label = Label(
            text=instructions if instructions else "No instructions available.",
            color=(0,0,0,1),
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
        scroll.scroll_y = 1  # Always start at the top

        # Images stacked vertically, much bigger
        img_vbox = BoxLayout(orientation='vertical', spacing=15, size_hint_y=None)
        for img_name in images:
            img_path = os.path.join(EXERCISE_IMAGES_DIR, img_name)
            if os.path.exists(img_path):
                img_vbox.add_widget(Image(source=img_path, size_hint=(None, None), size=(320, 220)))
            else:
                img_vbox.add_widget(Label(text="No image", size_hint=(None, None), size=(320, 220), color=(0,0,0,1)))
        img_vbox.height = len(images) * 235

        layout = BoxLayout(orientation='vertical', spacing=10, padding=[10,10,10,10])
        layout.add_widget(Label(text="Instructions:", color=(0,0,0,1), size_hint_y=None, height=30, bold=True))
        layout.add_widget(scroll)
        layout.add_widget(Label(text="Images:", color=(0,0,0,1), size_hint_y=None, height=30, bold=True))
        layout.add_widget(img_vbox)

        popup = Popup(title=display_name(ex_name), content=layout, size_hint=(0.98, 0.85))
        popup.open()

    def finish_workout(self):
        progress = load_progress()
        entry = {
            "workout": self.workout["name"],
            "exercises": list(self.workout["exercises"]),  # Save current exercises
            "timestamp": datetime.datetime.now().isoformat()
        }
        progress.append(entry)
        save_progress(progress)
        popup = Popup(title="Workout Finished", content=Label(text="Workout marked as finished!"), size_hint=(0.7, 0.3))
        popup.open()

class TipsScreen(Screen):
    pass

class WorkItApp(App):
    def build(self):
        Window.clearcolor = (0.12, 0.12, 0.12, 1)
        Window.size = (360, 640)
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(MyWorkoutsScreen(name='my_workouts'))
        sm.add_widget(WorkoutCreationScreen(name='workout_creation'))
        sm.add_widget(TipsScreen(name='tips'))
        sm.add_widget(WorkoutDetailScreen(name='workout_detail'))
        return sm

if __name__ == "__main__":
    WorkItApp().run()