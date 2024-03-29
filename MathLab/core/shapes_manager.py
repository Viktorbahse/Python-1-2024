from sympy import symbols, lambdify
from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import *


SEARCH_RADIUS = 5


class ShapesManager:
    def __init__(self):
        self.shapes = {Point: [], Segment: [], Polygon: [], Line: [], Ray: [], Circle: [], Inf: []}  # Словарик для хранения фигур
        self.temp_segments = []
        self.temp_lines = []
        self.temp_rays = []
        self.temp_circles = []
        self.selected_points = []
        
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

    @staticmethod
    def distance(array_points: []):
        a = array_points[0]
        b = array_points[1]
        dist = ((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5
        return dist

    def add_selected_point(self, point):
        self.selected_points.append(point)

    def clear_selected_points(self):
        self.selected_points = []

    def add_temp_segment(self, shape):
        self.temp_segments.append(shape)

    def add_temp_line(self, shape):
        self.temp_lines.append(shape)

    def add_temp_ray(self, shape):
        self.temp_rays.append(shape)

    def add_temp_circle(self, shape):
        self.temp_circles.append(shape)

    def clear_temp_segments(self):
        self.temp_segments = []

    def clear_temp_lines(self):
        self.temp_lines = []

    def clear_temp_rays(self):
        self.temp_rays = []

    def clear_temp_circles(self):
        self.temp_circles = []
