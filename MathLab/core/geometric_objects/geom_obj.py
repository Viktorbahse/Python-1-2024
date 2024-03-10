import sympy as sp
class Shape:
    def __init__(self, color="black"):
        self.color = color

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color
