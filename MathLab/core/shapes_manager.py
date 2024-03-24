from sympy import symbols, lambdify
from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import *


SEARCH_RADIUS = 5


class ShapesManager:
    def __init__(self):
        self.shapes = {Point: [], Segment: [], Polygon: [], Line: [], Ray: [] }  # Словарик для хранения фигур
        self.temp_segments = []  # Список для хранения временных отрезков, таких как "предпросмотр"
        self.temp_lines = []
        self.temp_rays = []
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

    def add_temp_segment(self, shape):
        self.temp_segments.append(shape)
    def add_temp_line(self,shape):
        self.temp_lines.append(shape)
    def add_temp_ray(self,shape):
        self.temp_rays.append(shape)


    def clear_temp_segments(self):
        self.temp_segments = []

    def clear_temp_lines(self):
        self.temp_lines =[]

    def clear_temp_rays(self):
        self.temp_rays =[]