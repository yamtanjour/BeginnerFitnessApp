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
from kivy.metrics import dp
from data_handling import load_workouts, load_exercises, save_progress, load_progress, EXERCISE_IMAGES_DIR, get_exercise_info, display_name, load_premade_workouts, ensure_json_file_exists   


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
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), spacing=dp(10), padding=[dp(5),0,dp(5),0])
            lbl = Label(
                text=display_name(ex),
                size_hint_x=0.6,
                halign='left',
                valign='middle',
                color=(1,1,1,1),
                text_size=(None, None),
                font_size=dp(20)
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
                color=(1,1,1,1),
                font_size=dp(16)
            )
            def on_info_touch(instance, touch, name=ex):
                if instance.collide_point(*touch.pos):
                    self.show_exercise_info(name)
            info_lbl.bind(on_touch_down=on_info_touch)
            row.add_widget(info_lbl)
            box.add_widget(row)
            box.add_widget(Widget(size_hint_y=None, height=dp(2)))

    def show_exercise_info(self, ex_name):
        ex_info = get_exercise_info(ex_name)
        if not ex_info:
            content = Label(text="No info found.", size_hint_y=None, height=40, color=(1,1,1,1))
            popup = Popup(title="Exercise Info", content=content, size_hint=(0.9, 0.7))
            popup.open()
            return
        images = ex_info.get("images", [])[:2]
        img_vbox = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None)
        for img_name in images:
            img_path = os.path.join(EXERCISE_IMAGES_DIR, img_name)
            if os.path.exists(img_path):
                img_vbox.add_widget(Image(source=img_path, size_hint=(None, None), size=(dp(320), dp(220))))
            else:
                img_vbox.add_widget(Label(text="No image", size_hint=(None, None), size=(dp(320), dp(220)), color=(1,1,1,1)))
        img_vbox.height = len(images) * dp(235)
        layout = BoxLayout(orientation='vertical', spacing=dp(10), padding=[dp(10),dp(10),dp(10),dp(10)])
        layout.add_widget(img_vbox)
        from kivy.uix.button import Button
        instr_btn = Button(text="Show Instructions", size_hint_y=None, height=dp(44))
        instr_btn.bind(on_release=lambda instance: self.show_instructions_only_popup(ex_name))
        layout.add_widget(instr_btn)
        popup = Popup(title=display_name(ex_name), content=layout, size_hint=(0.98, 0.85))
        popup.open()

    def show_instructions_only_popup(self, ex_name):
        ex_info = get_exercise_info(ex_name)
        instructions = "\n".join(ex_info.get("instructions", [])) if ex_info else "No instructions available."
        from kivy.uix.button import Button
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.scrollview import ScrollView
        instr_label = Label(
            text=instructions,
            color=(1,1,1,1),
            halign='left',
            valign='top',
            size_hint_y=None
        )
        def update_text_size(instance, value):
            instance.text_size = (instance.width, None)
            instance.texture_update()
            instance.height = instance.texture_size[1]
        instr_label.bind(width=update_text_size)
        instr_label.text_size = (400, None)
        instr_label.height = instr_label.texture_size[1]
        scroll = ScrollView(size_hint=(1, 1), bar_width=10)
        scroll.add_widget(instr_label)
        layout = BoxLayout(orientation='vertical', padding=[dp(24),dp(24),dp(24),dp(24)], spacing=dp(18))
        layout.add_widget(Label(text="Instructions", color=(0.2,0.8,0.4,1), font_size=dp(22), bold=True, size_hint_y=None, height=dp(36)))
        layout.add_widget(scroll)
        btn_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50), padding=[0,dp(10),0,0])
        btn_box.add_widget(Widget())
        close_btn = Button(text="Close", size_hint_x=None, width=dp(120), height=dp(44))
        close_btn.bind(on_release=lambda instance: popup.dismiss())
        btn_box.add_widget(close_btn)
        btn_box.add_widget(Widget())
        layout.add_widget(btn_box)
        popup = Popup(title=f"{display_name(ex_name)} Instructions", content=layout, size_hint=(0.8, 0.6))
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