from core.geometric_objects.geom_obj import *
from core.exception.exception import CustomException
import sympy as sp


class Circle(Shape):
    def __init__(self, points=None, color=(17, 167, 234, 255), width=1.5, owner=None):
        super().__init__(color=color)
        self.point_1 = None
        self.point_2 = None
        self.circle = None
        self.points = []

        # У нас может быть окружность, у которой радиус пока неизвестен
        if points is not None:
            self.add_point(points[0])
            self.add_point(points[1])

        self.width = width
        self.point_color = (0, 102,204, 255)
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


class Polygon(Shape):
    def __init__(self, points=None, color=(255, 0, 0, 255)):
        super().__init__(color)
        if points is None:
            self.points = []
        else:
            self.points = points

        self.point_color = self.color
        self.line_color = self.color

    def add_point(self, point):
        self.points.append(point)


class Square(Shape):
    def __init__(self, point_a: Point, point_b: Point, color="black"):
        try:
            if point_a.point.x == point_b.point.x and point_a.point.y == point_b.point.y:
                raise CustomException("The vertices of the square coincide")
        except CustomException as e:
            print(f"Произошла ошибка: {e.message}")
        else:
            super().__init__(color)
            self.point_a = point_a
            self.point_b = point_a
            self.side = sp.sqrt((point_b.point.x - point_a.point.x) ** 2 + (point_b.point.y - point_a.point.y) ** 2)

    def area(self):
        return self.side * self.side

    def perimeter(self):
        return 4 * self.side


class Function(Shape):
    def __init__(self, latex_string, color=(255, 0, 0, 255), width=1.5):
        self.expr = sp.sympify(latex_string)
        self.width = width
        super().__init__(color)
    def evaluate(self, x_value):
        y_value = self.expr.subs('x', x_value)
        return y_value


class Triangle(Shape):
    def __init__(self, x1_, y1_, x2_, y2_, x3_, y3_, color="black"):
        try:
            if (x1_ == x2_ and y1_ == y2_) or (x1_ == x3_ and y1_ == y3_) or (x3_ == x2_ and y3_ == y2_):
                raise CustomException("The vertices of the triangle coincide")
        except CustomException as e:
            print(f"Произошла ошибка: {e.message}")
        else:
            super().__init__(color)
            self.x1 = x1_
            self.y1 = y1_
            self.x2 = x2_
            self.y2 = y2_
            self.x3 = x3_
            self.y3 = y3_
            self.a = sp.sqrt((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)
            self.b = sp.sqrt((self.x3 - self.x2) ** 2 + (self.y3 - self.y2) ** 2)
            self.c = sp.sqrt((self.x1 - self.x3) ** 2 + (self.y1 - self.y3) ** 2)

    def area(self):
        s = (self.a + self.b + self.c) / 2
        area = sp.sqrt(s * (s - self.a) * (s - self.b) * (s - self.c))
        return area

    def perimeter(self):
        return self.a + self.b + self.c

# FIXME Вынести из __init__ (try, except) в отдельную функцию
# FIXME Заменить везде color="цвет", на color=(r, g, b, прозрачность)
