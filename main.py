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
from MyWorkouts import MyWorkoutsScreen
from Progress import ProgressScreen
from Stats import StatsScreen
from WorkoutCreation import WorkoutCreationScreen
from WorkoutDetail import WorkoutDetailScreen
from PremadePopup import PremadePopup
from GreenButton import GreenButton
from kivy.core.window import Window
from PIL import Image as PILImage
from kivy.properties import StringProperty

def crop_to_aspect(img_path, target_ratio, save_path):
    img = PILImage.open(img_path)
    iw, ih = img.size
    img_ratio = iw / ih

    if img_ratio > target_ratio:
        # Image is wider than target: crop width
        new_width = int(ih * target_ratio)
        left = (iw - new_width) // 2
        img = img.crop((left, 0, left + new_width, ih))
    else:
        # Image is taller than target: crop height
        new_height = int(iw / target_ratio)
        top = (ih - new_height) // 2
        img = img.crop((0, top, iw, top + new_height))
    img.save(save_path)

# Usage:
screen_width, screen_height = Window.size
target_ratio = screen_width / screen_height
crop_to_aspect("background1.jpg", target_ratio, "bg1.jpg")
crop_to_aspect("background2.jpg", target_ratio, "bg2.jpg")
crop_to_aspect("background3.jpg", target_ratio, "bg3.jpg")
crop_to_aspect("background4.jpg", target_ratio, "bg4.jpg")
crop_to_aspect("background5.jpg", target_ratio, "bg5.jpg")
crop_to_aspect("background6.jpg", target_ratio, "bg6.jpg")
class HomeScreen(Screen):
    pass

class TipsScreen(Screen):
    tips_text = StringProperty("")

    def on_pre_enter(self):
        try:
            with open("tips.txt", "r", encoding="utf-8") as f:
                self.tips_text = f.read()
        except Exception as e:
            self.tips_text = "Could not load tips: " + str(e)

class GreenButton(Button):
    pass

class WorkItApp(App):
    def build(self):
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
