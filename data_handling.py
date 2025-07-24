import os
import json
import shutil
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.core.window import Window


WORKOUTS_FILE = "workouts.json"
EXERCISES_FILE = "all_exercises.json"
PROGRESS_FILE = "progress.json"
PREMADE_FILE = "premade_workouts.json"
EXERCISE_IMAGES_DIR = "exercise_images"

def ensure_json_file_exists(filename):
    app = App.get_running_app()
    dst = os.path.join(app.user_data_dir, filename)
    if not os.path.exists(dst):
        src = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(src):
            shutil.copyfile(src, dst)
        else:
            with open(dst, "w") as f:
                f.write("[]")
    return dst

def load_workouts():
    path = ensure_json_file_exists(WORKOUTS_FILE)
    with open(path, "r") as f:
        return json.load(f)

def save_workouts(workouts):
    path = ensure_json_file_exists(WORKOUTS_FILE)
    with open(path, "w") as f:
        json.dump(workouts, f, indent=2)

def load_exercises():
    path = ensure_json_file_exists(EXERCISES_FILE)
    with open(path, "r") as f:
        return json.load(f)

def load_progress():
    path = ensure_json_file_exists(PROGRESS_FILE)
    with open(path, "r") as f:
        return json.load(f)

def save_progress(progress):
    path = ensure_json_file_exists(PROGRESS_FILE)
    with open(path, "w") as f:
        json.dump(progress, f, indent=2)

def load_premade_workouts():
    path = ensure_json_file_exists(PREMADE_FILE)
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