from sympy import symbols, lambdify
from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import *
from tests.timing import *

SEARCH_RADIUS = 5


class ShapesManager:
    def __init__(self):
        # Словарик для хранения фигур
        self.shapes = {Point: [], Segment: [], Polygon: [], Line: [], Ray: [], Circle: [], Inf: [], Function: []}
        # Словарик для временных фигур
        self.temp_shapes = {Segment: [], Line: [], Ray: [], Circle: []}
        self.selected_points = []

    def add_shape(self, shape):
        if type(shape) == Point:
            shape.creating_name()
        self.shapes[type(shape)].append(shape)

    def remove_shape(self, shape):
        if shape in self.shapes[type(shape)]:
            self.shapes[type(shape)].remove(shape)
        if type(shape) != Point:
            shape.__del__()

    def add_temp_shape(self, shape):
        shape_type = type(shape)
        self.temp_shapes[shape_type].append(shape)

    def clear_temp_shapes(self, shape_type=None):
        if shape_type:
            self.temp_shapes[shape_type].clear()
        else:
            for shapes in self.temp_shapes.values():
                shapes.clear()

    def add_selected_point(self, point):
        self.selected_points.append(point)

    def clear_selected_points(self):
        self.selected_points = []

    def find_closest_shape(self, x, y, radius=SEARCH_RADIUS):
        # Находит ближайший объект и расстояние до него
        closest_shape = None
        min_distance = float('inf')
        all_shapes = []

        for shape_list in self.shapes.values():
            for shape in shape_list:
                distance = shape.distance_to_shape(x, y)  # Этот метод должен вычислять расстояние от точки до объекта
                if distance < radius:
                    all_shapes.append(shape)
                    if distance < min_distance:
                        min_distance = distance
                        closest_shape = shape

        return closest_shape, min_distance, all_shapes

    @staticmethod
    def distance(array_points: []):
        a = array_points[0]
        b = array_points[1]
        dist = ((a.entity.x - b.entity.x) ** 2 + (a.entity.y - b.entity.y) ** 2) ** 0.5
        return dist
