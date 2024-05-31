from core.geometric_objects.geom_obj import *
from core.exception.exception import CustomException
import sympy as sp
from sympy.calculus.util import singularities


class Circle(Shape):
    def __init__(self, points=None, color=(255, 50, 25, 255), width=1.5, owner=None):
        super().__init__(color=color, width=width)
        self.points = []

        # У нас может быть окружность, у которой радиус пока неизвестен
        if points is not None:
            self.add_point(points[0])
            self.add_point(points[1])

        self.point_color = color
        self.owner = owner if owner is not None else []
        for shape in self.owner:
            self.set_color(shape.line_color)
        self.typeShape = 'Circle'

    def __del__(self):
        super().__del__()
        self.points = None

    def get_info(self):
        info = super().get_info()
        info['points'] = self.points
        info['point_color'] = self.point_color
        return info

    def add_point(self, point, is_primary=True):
        super().add_point(point, is_primary=is_primary)
        if len(self.points) == 2:
            center = self.points[0].entity
            point_on_circle = self.points[1].entity
            radius = center.distance(point_on_circle)
            self.entity = sp.Circle(center, radius)

    def distance_to_shape(self, x, y):
        # Считаем расстояние от центра круга до нужной точки
        center = self.entity.center
        radius = self.entity.radius
        distance_from_center = center.distance(sp.Point(float(x), float(y)))
        # Сам расчет
        distance_to_circle = abs(distance_from_center - radius)
        return float(distance_to_circle)

    def projection_onto_shape(self, point):  # Проекция
        center = sp.Point2D(self.entity.center)
        mouse_point = sp.Point2D(point)
        # Вектор от центра круга до данной точки
        vector_to_point = mouse_point - center
        length = sp.sqrt(vector_to_point[0] ** 2 + vector_to_point[1] ** 2)
        # Нормализуем вектор
        normalized_vector = sp.Point2D(vector_to_point[0] / length, vector_to_point[1] / length)
        # Находим точку на окружности, находящуюся на линии, соединяющей центр круга и данную точку
        projection = center + normalized_vector * self.entity.radius
        return projection

    def contains(self, point):  # Содержится ли точка
        return self.center.distance(point) == self.radius

    def set_name(self, new_name):
        pass


class Polygon(Shape):
    def __init__(self, points=None, color=(255, 200, 0, 255), owner=None):
        super().__init__(color=color)
        self.finished = False
        if points is None:
            self.points = []
        else:
            self.points = points
        self.point_color = self.color
        self.line_color = self.color
        self.owner = owner if owner is not None else []
        self.typeShape = 'Polygon'

    def __del__(self):
        super().__del__()
        self.points = None

    def get_info(self):
        info = super().get_info()
        info['points'] = self.points
        info['point_color'] = self.point_color
        info['line_color'] = self.line_color
        return info

    def distance_to_shape(self, x, y):
        point_to_check = sp.Point(x, y)

        # Инициализируем первую сторону полигона
        p1 = self.points[-1].entity  # Предполагаем, что entity - это объект sp.Point
        p2 = self.points[0].entity
        side = sp.Segment(p1, p2)
        min_distance = side.distance(point_to_check)  # Устанавливаем расстояние для первой стороны

        # Перебираем все стороны полигона
        for i in range(1, len(self.points)):
            p1 = p2
            p2 = self.points[i].entity
            side = sp.Segment(p1, p2)
            current_distance = side.distance(point_to_check)
            if current_distance < min_distance:
                min_distance = current_distance  # Обновляем минимальное расстояние

        return float(min_distance)  # Возвращаем минимальное расстояние как число

    def set_name(self, new_name):
        pass


class Function(Shape):
    def __init__(self, string=""):
        super().__init__()
        self.correct = False
        self.color = (255, 0, 0, 255)
        self.entity = string
        self.width = 1.5
        self.x = sp.symbols('x')
        self.type = None
        self.typeShape = 'Function'

    def reset(self, string):
        self.entity = string
        try:
            self.expr = sp.sympify(string) if isinstance(string, str) else string  # Преобр. строку в мат выражение
            self.f = sp.lambdify(self.x, self.expr, 'numpy')
            self.discontinuity_points = sp.singularities(self.expr, self.x)
            self.correct = True
            self.test_type()
        except:
            self.correct = False
            self.type = "False"

    def test_type(
            self):  # Попытка оптимизировать рисование функций, заранее определяя их тип. Оптимизация работает только для прямых.
        diff = sp.diff(self.expr, self.x)
        if diff == 0:
            self.type = "const"
            return
        diff = sp.diff(diff, self.x)
        if diff == 0:
            self.type = "line"
            return
        diff = sp.diff(diff, self.x)
        if diff == 0:
            self.type = "parabole"
            return
        if 0 == sp.diff(sp.diff(sp.diff(sp.diff(diff, self.x), self.x), self.x), self.x):
            self.type = "polinom"
        self.type = "Hard"

    def evaluate(self, point):  # Считаем значения функции, возможны вылеты, если y_value содержит мнимую часть.
        try:
            y_value = self.expr.subs('x', point)
            return float(y_value)
        except:
            return None

    def intersection(self, func):  # Находим точки пересечения, функций, если можем:)
        try:
            solves = sp.solve(self.expr - func.expr, sp.symbols('x'))
            solves2 = []
            for x in solves:
                if sp.simplify(x).is_real:
                    solves2.append(x)
            return solves2
        except:
            return []

    def is_defined(self, point):  # Проверяем определена ли функция в точке и является ли ее значение вещественным.
        try:
            value = self.expr.subs(self.expr.args[0], point)
            return sp.simplify(value).is_real
        except:
            return False

    def set_name(self, new_name):
        pass
