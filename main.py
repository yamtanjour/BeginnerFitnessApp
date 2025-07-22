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
from data_handling import display_name, load_exercises, save_workouts, load_workouts, load_premade_workouts
WORKOUTS_FILE = "workouts.json"
EXERCISES_FILE = "all_exercises.json"
PROGRESS_FILE = "progress.json"
PREMADE_FILE = "premade_workouts.json"
EXERCISE_IMAGES_DIR = "exercise_images"
from MyWorkouts import MyWorkoutsScreen
from Progress import ProgressScreen
from Stats import StatsScreen
from WorkoutCreation import WorkoutCreationScreen
from WorkoutDetail import WorkoutDetailScreen
from PremadePopup import PremadePopup

class HomeScreen(Screen):
    pass

class TipsScreen(Screen):
    pass

class GreenButton(Button):
    pass

class WorkItApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.2, 0.5, 1)
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
