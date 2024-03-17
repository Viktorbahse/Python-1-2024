import sympy as sp
import math


class Shape:
    def __init__(self, color=(0, 0, 0, 255)):  # rgb + прозрачность
        self.color = color

    def set_color(self, color):
        if color is not None:
            self.color = color


class Point(Shape):
    def __init__(self, x, y, color=(71, 181, 255, 255), owner=[]):
        super().__init__(color=color)
        self.point = sp.Point(x, y)
        self.radius = 5
        self.owner = owner  # Принадлежности
        for shape in self.owner:
            self.set_color(shape.point_color)

    def add_to_owner(self, owner):
        self.owner.append(owner)
        self.set_color(owner.point_color)

    def distance(self, other_point):
        return self.point.distance(other_point.point)

    def contains_point(self, x, y, check_radius=5):
        distance = math.sqrt((self.point.x - x) ** 2 + (self.point.y - y) ** 2)
        return distance <= check_radius


# class Line(Shape):
#     def __init__(self, x1, y1, x2, y2, color="black"):
#         super().__init__(color)
#         self.x1 = x1
#         self.y1 = y1
#         self.x2 = x2
#         self.y2 = y2


class Line(Shape):
    def __init__(self, a: Point,  b: Point, color=(6, 40, 61, 200), width=1.5, owner=[]):
        super().__init__(color=color)
        self.line = sp.Line(a.point, b.point)
        self.x1 = a.point.x
        self.y1 = a.point.y
        self.x2 = b.point.x
        self.y2 = b.point.y
        self.width = width
        self.owner = owner
        for shape in self.owner:
            self.set_color(shape.point_color)

    def add_to_owner(self, owner):
        self.owner.append(owner)
        self.set_color(owner.line_color)

# class Line(Shape):
#     def __init__(self, a: Point, b:Point, color="black"):
#         self.line = sp.Line(a.point, b.point)
#         self.color = color
#
#     def slope(self):
#         return self.line.slope
#
#     def equation(self):
#         return self.line.equation()
