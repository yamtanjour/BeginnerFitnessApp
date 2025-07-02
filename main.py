from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

class HomeScreen(Screen):
    pass

class MyWorkoutsScreen(Screen):
    pass

class WorkItApp(App):
    def build(self):
        Window.clearcolor = (0.12, 0.12, 0.12, 1)
        Window.size = (360, 640)
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))  # <-- use 'home'
        sm.add_widget(MyWorkoutsScreen(name='my_workouts'))
        return sm
    
if __name__ == "__main__":
    WorkItApp().run()