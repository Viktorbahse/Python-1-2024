from core.geometric_objects.geom_obj import *
from core.exception.exception import CustomException
import sympy as sp
from sympy.calculus.util import singularities


class Circle(Shape):
    def __init__(self, points=None, color=(255, 50, 25, 255), width=1.5, owner=None):  # (17, 167, 234, 255)
        super().__init__(color=color)
        self.point_1 = None
        self.point_2 = None
        self.circle = None
        self.points = []

        # У нас может быть окружность, у которой радиус пока неизвестен
        if points is not None:
            self.add_point(points[0])
            self.add_point(points[1])

        self.width = width
        self.point_color = color  # (0, 102, 204, 255)
        self.owner = owner if owner is not None else []
        for shape in self.owner:
            self.set_color(shape.point_color)

    def add_point(self, point):
        self.points.append(point)
        if len(self.points) == 2:
            self.point_1 = self.points[0]
            self.point_2 = self.points[1]
            self.segment = sp.Line(self.point_1.point, self.point_2.point)

    def add_to_owner(self, owner):
        self.owner.append(owner)
        self.set_color(owner.line_color)


class Polygon(Shape):
    def __init__(self, points=None, color=(255, 200, 0, 255)):
        self.finished = False
        super().__init__(color)
        if points is None:
            self.points = []
        else:
            self.points = points

        self.point_color = self.color
        self.line_color = self.color

    def add_point(self, point):
        self.points.append(point)

    def closest_side(self, x, y):
        p1 = sp.Point(self.points[len(self.points) - 1].x, self.points[len(self.points) - 1].y)
        p2 = sp.Point(self.points[0].x, self.points[0].y)
        side = sp.Segment(p1, p2)
        for i in range(1, len(self.points)):
            p1 = p2
            p2 = sp.Point(self.points[i].x, self.points[i].y)
            temp_side = sp.Segment(p1, p2)
            if side.distance(sp.Point(x, y)) > temp_side.distance(sp.Point(x, y)):
                side = temp_side
        return side


class Function(Shape):
    def __init__(self, color=(255, 0, 0, 255), width=1.5):
        self.width = width
        x = sp.symbols('x')
        self.f = sp.exp(x)
        self.points_of_discontinuity = singularities(self.f, x)
        super().__init__(color)

    def evaluate(self, x_value):
        y_value = self.expr.subs('x', x_value)
        return y_value
