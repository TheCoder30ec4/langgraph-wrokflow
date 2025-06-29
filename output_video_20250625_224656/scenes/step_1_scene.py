
from manim import *

class ErrorScene(Scene):
    def construct(self):
        text = Text("Error generating animation")
        self.play(Write(text))
        self.wait(2)
        