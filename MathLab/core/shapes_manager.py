from sympy import symbols, lambdify
from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import *


SEARCH_RADIUS = 5


class ShapesManager:
    def __init__(self):
        self.shapes = {Point: [], Segment: [], Polygon: []}  # Словарик для хранения фигур
        self.temp_items = []  # Список для хранения временных фигур, таких как "предпросмотр"
        x = symbols('x')
        f = x ** 2 - 4 * x + 4
        self.some = [lambdify(x, f, 'numpy')]

    def add_shape(self, shape):
        self.shapes[type(shape)].append(shape)

    def remove_shape(self, shape):
        if shape in self.shapes[type(shape)]:
            if shape == Point:  # Метод удаления работает только для Point
                self.shapes[type(shape)].remove(shape)

    def find_shape(self, x, y, radius=SEARCH_RADIUS):
        for shape in self.shapes[Point]:
            if shape.contains_point(x, y, radius):
                return shape
        return

    def find_closest_point(self, x, y, radius=SEARCH_RADIUS):
        # Поиск ближайшей точки в заданном радиусе
        for shape in self.shapes[Point]:
            if shape.contains_point(x, y, radius):
                return shape
        return None

    def add_temp_line(self, shape):
        self.temp_items.append(shape)

    def clear_temp_lines(self):
        self.temp_items = []
