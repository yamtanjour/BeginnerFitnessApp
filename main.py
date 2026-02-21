import os
import datetime
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from PIL import Image as PILImage
from data.data_handling import display_name, load_exercises, save_workouts, load_workouts, load_premade_workouts
from screens.MyWorkouts import MyWorkoutsScreen
from screens.Progress import ProgressScreen
from screens.Stats import StatsScreen
from screens.WorkoutCreation import WorkoutCreationScreen
from screens.WorkoutDetail import WorkoutDetailScreen
from screens.PremadeScreen import PremadeScreen
from components.GreenButton import GreenButton

#Start
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
crop_to_aspect("assets/backgrounds/background1.jpg", target_ratio, "assets/backgrounds/bg1.jpg")
crop_to_aspect("assets/backgrounds/background2.jpg", target_ratio, "assets/backgrounds/bg2.jpg")
crop_to_aspect("assets/backgrounds/background3.jpg", target_ratio, "assets/backgrounds/bg3.jpg")
crop_to_aspect("assets/backgrounds/background4.jpg", target_ratio, "assets/backgrounds/bg4.jpg")
crop_to_aspect("assets/backgrounds/background5.jpg", target_ratio, "assets/backgrounds/bg5.jpg")
crop_to_aspect("assets/backgrounds/background6.jpg", target_ratio, "assets/backgrounds/bg6.jpg")

class HomeScreen(Screen):
    tips_list = [
        "Always warm up for 5–10 minutes before lifting weights. (e.g., brisk walking, cycling, or dynamic stretches)",
        "Focus on proper form before increasing the weight. Use mirrors or ask staff to help you correct your posture.",
        "Stick to full-body workouts during your first few weeks. They build a foundation and help your body adjust.",
        "Use machines when starting — they guide movement and reduce injury risk.",
        "Start with 2–3 workouts per week, then gradually increase to 4–5.",
        "Take at least one rest day between strength sessions to recover.",
        "Drink water during your workout — bring a refillable bottle.",
        "Wear clean gym shoes and bring a towel every session.",
        "Log each workout, even if it's short — tracking builds consistency.",
        "Don't skip stretching after a workout — it helps with recovery.",
        "Rest 30–60 seconds between sets; longer (90s–2 mins) for heavier lifts.",
        "Combine cardio and strength training for better overall results.",
        "Avoid training the same muscle group two days in a row.",
        "Clean equipment after use — wipe down benches and machines.",
        "Re-rack your weights when you're done — keep the gym safe and tidy.",
        "Focus on controlled movement — no need to rush reps.",
        "Don’t skip leg day — leg exercises build total-body strength.",
        "Set short-term goals (e.g., 3 workouts this week) to stay motivated.",
        "Track how you feel after each workout — tired, sore, strong, etc.",
        "Get 7–9 hours of sleep per night — recovery happens when you rest."
    ]

    @property
    def daily_tip(self):
        today = datetime.date.today().toordinal()
        return self.tips_list[today % len(self.tips_list)]


class WorkItApp(App):
    title = 'WorkIt'
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(MyWorkoutsScreen(name='my_workouts'))
        sm.add_widget(WorkoutCreationScreen(name='workout_creation'))
        sm.add_widget(PremadeScreen(name='premade'))
        sm.add_widget(WorkoutDetailScreen(name='workout_detail'))
        sm.add_widget(ProgressScreen(name='progress'))
        sm.add_widget(StatsScreen(name='stats'))
        return sm

if __name__ == "__main__":
    WorkItApp().run()
