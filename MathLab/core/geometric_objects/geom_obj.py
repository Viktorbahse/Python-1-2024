import sympy as sp
from abc import ABC, abstractmethod


class Shape(ABC):
    def __init__(self, entity=None, color=(0, 0, 0, 255), width=1.5):  # rgb + прозрачность
        self.color = color
        self.entity = entity
        self.width = width

    def set_color(self, color):
        if color is not None:
            self.color = color

    def distance_to_shape(self, x, y):
        return self.entity.distance(sp.Point(x, y))

    def add_dependent_object(self, owner):
        self.dependent_objects.append(owner)
        self.set_color(owner.line_color)

    @abstractmethod
    def set_name(self, new_name):
        pass

    def add_point(self, point):
        self.points.append(point)


class Inf:
    def __init__(self, x, y, message):
        self.x = x
        self.y = y
        self.message = message


class Point(Shape):
    count = 0

    def __init__(self, x, y, color=(71, 181, 255, 255), owner=None):
        super().__init__(sp.Point(x, y), color=color)
        self.name = chr(Point.count % 26 + 65)
        if Point.count > 25:
            self.name += str(Point.count // 26)
        # Мне все-таки нужны self.x, self.y. Именно их я беру для отрисовки
        self.radius = 5
        self.dependent_objects = owner if owner is not None else []  # Определяем список
        for shape in self.dependent_objects:
            self.set_color(shape.point_color)
        Point.count += 1

    def __del__(self):
        self.previous_name()

    def previous_name(self):
        Point.count -= 1

    def next(self):
        Point.count += 1

    def add_dependent_object(self, owner):
        self.dependent_objects.append(owner)
        if len(self.dependent_objects) == 1:
            self.set_color(self.dependent_objects[0].point_color)
        else:
            color = [0, 0, 0, 0]
            for i in range(len(color)):
                color[i] += (owner.point_color[i] + self.color[i]) // 2
            self.set_color(color)

    def add_point(self, point):
        pass

    def set_name(self, new_name):
        pass


class Segment(Shape):
    def __init__(self, points=None, color=(23, 52, 175, 255), width=1.5, owner=None):
        super().__init__(color=color)
        self.points = []
        self.dependent_objects = owner if owner is not None else []
        # У нас может быть отрезок, которому не передали точки
        if points is not None:
            self.add_point(points[0])
            self.add_point(points[1])

        self.point_color = color  # (255, 220, 51, 255)
        self.dependent_objects = owner if owner is not None else []
        for shape in self.dependent_objects:
            self.set_color(shape.point_color)

    def add_point(self, point):
        super().add_point(point=point)
        if len(self.points) == 2:
            self.entity = sp.Segment(self.points[0].entity, self.points[1].entity)

    def set_name(self, new_name):
        pass


class Line(Shape):
    def __init__(self, points=None, color=(143, 0, 255, 255), width=1.5, owner=None):  # (51, 51, 255, 255)
        super().__init__(color=color, width=width)
        self.points = []

        # У нас может быть прямая, которому не передали точки
        if points is not None:
            self.add_point(points[0])
            self.add_point(points[1])

        self.point_color = color  # (127, 0, 255, 255)
        self.dependent_objects = owner if owner is not None else []
        for shape in self.dependent_objects:
            self.set_color(shape.point_color)

    def add_point(self, point):
        self.points.append(point)
        if len(self.points) == 2:
            self.entity = sp.Line(self.points[0].entity, self.points[1].entity)

    def set_name(self, new_name):
        pass


class Ray(Shape):
    def __init__(self, points=None, color=(206, 82, 200, 255), width=1.5, owner=None):  # (255, 51, 153, 255)
        super().__init__(color=color, width=width)
        self.points = []

        # У нас может быть луч, которому не передали точки
        if points is not None:
            self.add_point(points[0])
            self.add_point(points[1])

        self.point_color = color  # (127, 0, 255, 255)
        self.dependent_objects = owner if owner is not None else []
        for shape in self.dependent_objects:
            self.set_color(shape.point_color)

    def add_point(self, point):
        super().add_point(point=point)
        if len(self.points) == 2:
            self.entity = sp.Segment(self.points[0].entity, self.points[1].entity)

    def set_name(self, new_name):
        pass
