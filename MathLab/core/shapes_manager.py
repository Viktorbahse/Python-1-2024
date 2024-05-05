from sympy import symbols, lambdify
from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import *
import sympy as sp

SEARCH_RADIUS = 5


class ShapesManager:
    def __init__(self):
        # Словарик для хранения фигур
        self.shapes = {Point: [], Segment: [], Polygon: [], Line: [], Ray: [], Circle: [], Inf: [], Function: []}
        self.functions = []  # Массив для функций.
        self.intersection_points = []  # Массив для точек пересечения.
        # Словарик для временных фигур
        self.temp_shapes = {Segment: [], Line: [], Ray: [], Circle: []}
        self.selected_points = []

    def resolve_intersections(self):  # Считаем точки пересечения, если можем:)
        self.intersection_points = []
        for i in range(len(self.functions)):
            if self.functions[i].corect:
                for j in range(i):
                    if self.functions[j].corect:
                        result = self.functions[i].intersection(self.functions[j])
                        for x in result:
                            y = self.functions[i].evaluate(x)
                            self.intersection_points.append(Point(x, y))
                            self.intersection_points[-1].set_name("")
                            self.intersection_points[-1].set_color([155, 155, 155, 255])
                            self.intersection_points[-1].radius = 3

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

    def find_closest_point(self, x, y, radius=SEARCH_RADIUS):
        # Поиск ближайшей точки в заданном радиусе
        closest_point = None
        distance = radius + 1
        for shape in self.shapes[Point]:
            if shape.distance_to_shape(x, y) < distance:
                distance = shape.distance_to_shape(x, y)
                closest_point = shape
        if distance < radius:
            return closest_point
        return None

    def find_closest_line(self, x, y, radius=SEARCH_RADIUS):
        closest_shape = None
        distance = radius + 1
        for shape in self.shapes[Line]:
            if len(shape.points) == 2 or shape.entity is not None:
                if shape.distance_to_shape(x, y) < distance:
                    closest_shape = shape.entity
                    distance = shape.distance_to_shape(x, y)
        for shape in self.shapes[Ray]:
            if len(shape.points) == 2:
                if shape.distance_to_shape(x, y) < distance:
                    closest_shape = shape.entity
                    distance = shape.distance_to_shape(x, y)
        for shape in self.shapes[Segment]:
            if len(shape.points) == 2:
                if shape.distance_to_shape(x, y) < distance:
                    closest_shape = shape.entity
                    distance = shape.distance_to_shape(x, y)
        for shape in self.shapes[Polygon]:
            if shape.finished:
                closest_temp_side = shape.closest_side(x, y)
                distance_to_closest_side = closest_temp_side.distance(sp.Point(x, y))
                if distance_to_closest_side < distance:
                    distance = distance_to_closest_side
                    closest_shape = closest_temp_side
        if distance < radius:
            return closest_shape
        return None

    def find_closest_shape(self, x, y, radius=SEARCH_RADIUS):
        # Находит ближайший объект и расстояние до него
        closest_shape = None
        min_distance = float('inf')

        for shape_list in self.shapes.values():
            for shape in shape_list:
                distance = shape.distance_to_shape(x, y)  # Этот метод должен вычислять расстояние от точки до объекта
                if distance < radius and distance < min_distance:
                    min_distance = distance
                    closest_shape = shape

        return closest_shape, min_distance

    @staticmethod
    def distance(array_points: []):
        a = array_points[0]
        b = array_points[1]
        dist = ((a.entity.x - b.entity.x) ** 2 + (a.entity.y - b.entity.y) ** 2) ** 0.5
        return dist
