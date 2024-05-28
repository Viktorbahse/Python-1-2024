from sympy import symbols, lambdify
from PyQt5.QtCore import pyqtSignal, QObject
from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import *

SEARCH_RADIUS = 5


class Communicate(QObject):
    shapesChanged = pyqtSignal()

class ShapesManager:
    def __init__(self):
        self.comm = Communicate()
        self.functions = []  # Массив для функций.
        # Словарик для хранения фигур
        self.shapes = {Point: [], Segment: [], Polygon: [], Line: [], Ray: [], Circle: [], Info: []}
        # Словарик для временных фигур
        self.temp_shapes = {Segment: [], Line: [], Ray: [], Circle: []}

        self.selected_points = []

    def add_shape(self, shape):
        self.shapes[type(shape)].append(shape)
        self.comm.shapesChanged.emit()

    def remove_shape(self, shape):
        changes = False
        if shape in self.shapes[type(shape)]:
            if shape == Point:  # Метод удаления работает только для Point
                self.shapes[type(shape)].remove(shape)
                changes = True
        if changes:
            self.comm.shapesChanged.emit()

    def find_shape(self, x, y, radius=SEARCH_RADIUS):
        for shape in self.shapes[Point]:
            if shape.contains_point(x, y, radius):
                return shape
        return

    def add_temp_shape(self, shape):
        shape_type = type(shape)
        self.temp_shapes[shape_type].append(shape)

    def clear_temp_shapes(self, shape_type=None):
        if shape_type:
            self.temp_shapes[shape_type].clear()
        else:
            for shapes in self.temp_shapes.values():
                shapes.clear()

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

# TODO: Перемести add_selected_point и clear_selected_points после clear_temp_shapes.
# Хочу, чтобы у нас была некоторая логика в порядке функций (когда я меняю порядок, то функции записываются на меня)