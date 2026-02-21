from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
from data.data_handling import load_premade_workouts, load_workouts, save_workouts, display_name


class PremadeScreen(Screen):
    def on_pre_enter(self):
        # populate the premade list
        premades = load_premade_workouts() or []
        box = self.ids.get('premade_list')
        if not box:
            return
        box.clear_widgets()
        for premade in premades:
            name = premade.get("name", "Unnamed")
            exercises = premade.get("exercises", [])
            entry = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(100), spacing=dp(8), padding=[dp(8), dp(8), dp(8), dp(8)])
            # title + short preview
            left = BoxLayout(orientation='vertical')
            lbl = Label(text=f"[b]{display_name(name)}[/b]", markup=True, size_hint_y=None, height=dp(32), halign='left', valign='middle')
            lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            left.add_widget(lbl)
            preview = ", ".join([display_name(e) for e in exercises[:6]])
            preview_lbl = Label(text=preview or "No exercises", size_hint_y=None, height=dp(48), halign='left', valign='top')
            preview_lbl.bind(size=lambda inst, val: setattr(inst, 'text_size', (inst.width, None)))
            left.add_widget(preview_lbl)
            entry.add_widget(left)
            # action buttons
            actions = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(220), spacing=dp(8))
            btn_import = Button(text="Import", size_hint_y=None, height=dp(40))
            btn_open = Button(text="Open in Creator", size_hint_y=None, height=dp(40))
            actions.add_widget(btn_import)
            actions.add_widget(btn_open)
            entry.add_widget(actions)

            def do_import(instance, w=premade):
                workouts = load_workouts() or []
                if not any(x.get("name") == w.get("name") for x in workouts):
                    workouts.append({"name": w.get("name"), "exercises": list(w.get("exercises", []))})
                    save_workouts(workouts)
                try:
                    self.manager.current = 'my_workouts'
                except Exception:
                    pass

            def do_open(instance, w=premade):
                try:
                    creator = self.manager.get_screen('workout_creation')
                    # expected method in WorkoutCreation to load premade selection
                    creator.load_premade_into_selection(w.get('name'), w.get('exercises', []))
                    self.manager.current = 'workout_creation'
                except Exception:
                    pass

            btn_import.bind(on_release=do_import)
            btn_open.bind(on_release=do_open)
            box.add_widget(entry)
