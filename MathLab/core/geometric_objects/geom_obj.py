import sympy as sp


class Point:
    def __init__(self, x, y, color="black"):
        self.point = sp.Point(x, y)
        self.color = color

    def distance(self, other_point):
        return self.point.distance(other_point.point)


class Line:
    def __init__(self, slope, intercept, color="black"):
        x, y = sp.symbols('x y')
        self.line = sp.Line(slope=slope, equation=sp.Eq(y, slope*x + intercept))
        self.color = color

    def slope(self):
        return self.line.slope

    def equation(self):
        return self.line.equation()


class Shape:
    def __init__(self, color="black"):
        self.color = color

    def get_color(self):
        return self.color

    def set_color(self, color):
        self.color = color
