import sympy as sp
from abc import ABC, abstractmethod


class Shape(ABC):
    def __init__(self, entity=None, color=(0, 0, 0, 255), width=1.5):  # rgb + прозрачность
        self.color = color
        self.entity = entity
        self.width = width

        self.owner = []  # Элементы, к которым принадлежит объект (владелец объекта)
        # Основные элементы, принадлежащие объекту (без них не живет, и основные не удаляются вместе с объектом)
        self.primary_elements = []
        # Второстепенные элементы, принадлежащие объекту (без них живет, и они удаляются вместе с объектом)
        self.secondary_elements = []

    def add_point(self, point, is_primary=True):
        # Добавляется точку к объекту
        self.points.append(point)
        if is_primary:  # Если основной  
            self.primary_elements.append(point)
        else:
            self.secondary_elements.append(point)

    def add_owner(self, owner):
        # Добавляет владельца
        if owner not in self.owner:
            self.owner.append(owner)
            self.update_color()

    def remove_owner(self, owner):
        # Удаляет владельца
        if owner in self.owner:
            self.owner.remove(owner)
            self.update_color()

    def add_primary_element(self, element):
        # Добавляет основной элемент (пока не исп)
        self.primary_elements.append(element)
        if self not in element.owner:
            element.add_owner(self)  # К этому элементу устанавливается нынешний объект как владелец

    def remove_primary_element(self, element):
        # Удаляет основной элемент
        if element in self.primary_elements:
            self.primary_elements.remove(element)
            element.remove_owner(self)

    def add_secondary_element(self, element):
        # Добавляет второстепенный элемент (пока не исп)
        self.secondary_elements.append(element)
        if self not in element.owner:
            element.add_owner(self)

    def remove_secondary_element(self, element):
        # Удаляет второстепенный элемент
        if element in self.secondary_elements:
            self.secondary_elements.remove(element)
            element.remove_owner(self)

    def update_color(self):
        # Устанавливает цвет, если есть несколько владельцев, то уст средний
        if len(self.owner) == 0:
            self.set_color((71, 181, 255, 255))
        elif len(self.owner) == 1:
            self.set_color(self.owner[0].point_color)
        else:
            color = [0, 0, 0, 0]
            for owner in self.owner:
                for i in range(len(color)):
                    color[i] += owner.point_color[i]

            num_colors = len(self.owner)
            for i in range(len(color)):
                color[i] //= num_colors
            self.set_color(color)

    def set_color(self, color):
        if color is not None:
            self.color = color

    def distance_to_shape(self, x, y):
        return self.entity.distance(sp.Point(float(x), float(y)))
        # TODO: (Vik76) Будет хорошо, если он будет между remove_secondary_element и update_color
        #  (там у нас будет блок вычислений)

    @abstractmethod
    def set_name(self, new_name):
        pass


class Inf:
    def __init__(self, x, y, message):
        self.x = x
        self.y = y
        self.message = message
        # TODO: (Vik76) Правильно доделай, тогда я смогу удалять и сообщения


class Point(Shape):
    count = 0

    def __init__(self, x, y, color=(71, 181, 255, 255), owner=None):
        super().__init__(sp.Point(x, y), color=color)

        self.name = chr(Point.count % 26 + 65)
        if Point.count > 25:
            self.name += str(Point.count // 26)

        self.radius = 5
        Point.count += 1
        self.owner = owner if owner is not None else []  # Определяем список
        self.update_color()

        # TODO: (Vik76) Имя точки в отдельную функцию надо вынести. Также пересмотри то, как у нас имя считается

    def __del__(self):
        self.previous_name()

    def previous_name(self):
        Point.count -= 1

    def next(self):
        Point.count += 1

    def add_point(self, point, is_primary=True):
        pass

    def set_name(self, new_name):
        pass


class Segment(Shape):
    def __init__(self, points=None, color=(23, 52, 175, 255), width=1.5, owner=None):
        super().__init__(color=color, width=width)
        self.points = []
        self.owner = owner if owner is not None else []
        # У нас может быть отрезок, которому не передали точки
        if points is not None:
            self.add_point(points[0])
            self.add_point(points[1])

        self.point_color = color
        for shape in self.owner:
            self.set_color(shape.point_color)

    def add_point(self, point, is_primary=True):
        super().add_point(point=point, is_primary=is_primary)
        if len(self.points) == 2:
            self.entity = sp.Segment(self.points[0].entity, self.points[1].entity)

    def set_name(self, new_name):
        pass


class Line(Shape):
    def __init__(self, points=None, color=(143, 0, 255, 255), width=1.5, owner=None):
        super().__init__(color=color, width=width)
        self.points = []

        # У нас может быть прямая, которому не передали точки
        if points is not None:
            self.add_point(points[0])
            self.add_point(points[1])

        self.point_color = color
        self.owner = owner if owner is not None else []
        for shape in self.owner:
            self.set_color(shape.point_color)

    def add_point(self, point, is_primary=True):
        super().add_point(point=point, is_primary=is_primary)
        if len(self.points) == 2:
            self.entity = sp.Line(self.points[0].entity, self.points[1].entity)

    def set_name(self, new_name):
        pass


class Ray(Shape):
    def __init__(self, points=None, color=(206, 82, 200, 255), width=1.5, owner=None):
        super().__init__(color=color, width=width)
        self.points = []

        # У нас может быть луч, которому не передали точки
        if points is not None:
            self.add_point(points[0])
            self.add_point(points[1])

        self.point_color = color
        self.owner = owner if owner is not None else []
        for shape in self.owner:
            self.set_color(shape.point_color)

    def add_point(self, point, is_primary=True):
        super().add_point(point=point, is_primary=is_primary)
        if len(self.points) == 2:
            self.entity = sp.Segment(self.points[0].entity, self.points[1].entity)

    def set_name(self, new_name):
        pass
