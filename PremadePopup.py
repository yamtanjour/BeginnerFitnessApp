import os
import re
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from data_handling import load_premade_workouts, display_name



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
