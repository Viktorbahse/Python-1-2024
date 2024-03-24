
import sympy as sp
import math


class Shape:
    def __init__(self, color=(0, 0, 0, 255)):  # rgb + прозрачность
        self.color = color

    def set_color(self, color):
        if color is not None:
            self.color = color


class Point(Shape):
    def __init__(self, x, y, color=(71, 181, 255, 255), owner=None):
        super().__init__(color=color)
        self.point = sp.Point(x, y)

        # Мне все-таки нужны self.x, self.y. Именно их я беру для отрисовки
        self.x = x
        self.y = y
        self.radius = 5
        self.owner = owner if owner is not None else []  # Определяем список
        for shape in self.owner:
            self.set_color(shape.point_color)

    def add_to_owner(self, owner):
        self.owner.append(owner)

        # Следующие строчки больше для отладки. Если точка принадлежит нескольким объектам, то у нее будет "средний" цвет
        if self.owner:
            color = [0, 0, 0, 0]
            for shape in self.owner:
                shape_color = shape.point_color
                for i in range(len(color)):
                    color[i] += shape_color[i]
            for i in range(len(color)):
                color[i] //= len(self.owner)
        # self.set_color(shape.point_color)
        self.set_color(color)

    def distance(self, other_point):
        return self.point.distance(other_point.point)

    def contains_point(self, x, y, check_radius=5):
        distance = math.sqrt((self.point.x - x) ** 2 + (self.point.y - y) ** 2)
        return distance <= check_radius


class Segment(Shape):
    def __init__(self, points=None, color=(6, 40, 61, 255), width=1.5, owner=None):
        super().__init__(color=color)
        self.point_1 = None
        self.point_2 = None
        self.segment = None
        self.points = []

        # У нас может быть отрезок, которому не передали точки
        if points is not None:
            self.add_point(points[0])
            self.add_point(points[1])

        self.width = width
        self.point_color = (255, 220, 51, 255)
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

class Line(Shape):
    def __init__(self, points=None, color=(51, 51, 255, 255), width=1.5, owner=None):
        super().__init__(color=color)
        self.point_1 = None
        self.point_2 = None
        self.line = None
        self.points = []

        # У нас может быть прямая, которому не передали точки
        if points is not None:
            self.add_point(points[0])
            self.add_point(points[1])

        self.width = width
        self.point_color = (127, 0, 255, 255)
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

class Ray(Shape):
    def __init__(self, points=None, color=(255, 51, 153, 255), width=1.5, owner=None):
        super().__init__(color=color)
        self.point_1 = None
        self.point_2 = None
        self.ray = None
        self.points = []

        # У нас может быть луч, которому не передали точки
        if points is not None:
            self.add_point(points[0])
            self.add_point(points[1])

        self.width = width
        self.point_color = (127, 0, 255, 255)
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
