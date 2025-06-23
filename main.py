from kivy.app import App
from kivy.core.window import Window

class WorkItApp(App):
    def build(self):
        Window.clearcolor = (0.12, 0.12, 0.12, 1)  # Even darker background
        Window.size = (360, 640)  # Portrait aspect ratio for desktop testing

if __name__ == "__main__":
    WorkItApp().run()