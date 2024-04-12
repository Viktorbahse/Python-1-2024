from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt
from core.shapes_manager import ShapesManager
from core.geometric_objects.figure import *
import math


class Canvas(QGraphicsScene):
    def __init__(self, width, height, parent=None, zoom_factor=50.0):
        super().__init__(parent)
        self.setSceneRect(0, 0, width - 2, height - 2)

        self.shapes_manager = ShapesManager()
        self.zoom_factor = zoom_factor
        self.grid_step = 1
        self.base_point = [0, 0]

        self.initial_scene_x1, _ = self.to_scene_coords(self.grid_step, 0)  # Координаты первой от базовой точки линии
        self.initial_scene_x2, _ = self.to_scene_coords(self.grid_step * 2, 0)  # Второй линии
        self.update_scene()  # Полное обновление сцены

    def to_logical_coords(self, scene_x, scene_y):
        center_x = self.sceneRect().width() / 2 + self.base_point[0]
        center_y = self.sceneRect().height() / 2 + self.base_point[1]
        logical_x = (scene_x - center_x) / self.zoom_factor
        logical_y = (center_y - scene_y) / self.zoom_factor
        return logical_x, logical_y

    def to_scene_coords(self, logical_x, logical_y):
        center_x = self.sceneRect().width() / 2 + self.base_point[0]
        center_y = self.sceneRect().height() / 2 + self.base_point[1]
        scene_x = logical_x * self.zoom_factor + center_x
        scene_y = center_y - logical_y * self.zoom_factor
        return scene_x, scene_y

    def set_zoom_factor(self, factor):
        self.zoom_factor = factor
        self.grid_step_setting()

    def grid_step_setting(self):  # настройка шага сетки
        scene_x1, _ = self.to_scene_coords(self.grid_step, 0)  # Первая линия
        scene_x2, _ = self.to_scene_coords(self.grid_step * 2, 0)  # Вторая линия
        if not ((scene_x2 <= self.initial_scene_x1) or (scene_x1 >= self.initial_scene_x2)):
            return
        if scene_x2 <= self.initial_scene_x1:
            # Условие для увеличения шага сетки
            self.grid_step *= 2
            self.grid_step = self.pretty_step_increase(self.grid_step)
        elif scene_x1 >= self.initial_scene_x2:
            # Условие для уменьшения шага сетки
            self.grid_step /= 2
            self.grid_step = self.pretty_step_decrease(self.grid_step)

        # Обновление начальных значений сценических координат
        self.initial_scene_x1, _ = self.to_scene_coords(self.grid_step, 0)
        self.initial_scene_x2, _ = self.to_scene_coords(self.grid_step * 2, 0)
        print(self.grid_step)

        # есть баг. При зуме далеко от б.т. шаг сетки считается не корректно
        #  (так как в формуле не учитвается, что мы можем перемещаться)

    def pretty_step_increase(self, step):
        # Определяет следующее большее "красивое" значение
        pretty_steps = [1, 2, 5]
        magnitude = 10 ** math.floor(math.log10(step))
        base_step = step / magnitude

        for pretty_step in pretty_steps:
            if base_step <= pretty_step:
                return pretty_step * magnitude
        return pretty_steps[0] * magnitude * 10

    def pretty_step_decrease(self, step):
        # Определяет следующее меньшее "красивое" значение
        pretty_steps = [5, 2, 1]
        magnitude = 10 ** math.floor(math.log10(step))
        base_step = step / magnitude

        for pretty_step in pretty_steps:
            if base_step >= pretty_step:
                return pretty_step * magnitude
        return pretty_steps[-1]  # Для случаев, когда шаг меньше минимального "красивого" значения

    def update_scene(self):
        self.clear()  # Очищаем
        self.draw_grid()  # Рисуем сетку
        self.draw_coordinate_axes()  # Рисуем оси координат
        self.draw_temp_shapes()  # Рисуем временные фигуры (пока только линии)
        self.draw_shapes()  # Рисуем постоянные фигуры

    def draw_coordinate_axes(self, color=(0, 0, 0, 255)):
        x1, y1 = self.to_logical_coords(self.sceneRect().width() / 2 + self.base_point[0], 0)
        x2, y2 = self.to_logical_coords(self.sceneRect().width() / 2 + self.base_point[0], self.sceneRect().height())
        self.draw_segment(Segment([Point(x1, y1), Point(x2, y2)], color))

        x1, y1 = self.to_logical_coords(0, self.sceneRect().height() / 2 + self.base_point[1])
        x2, y2 = self.to_logical_coords(self.sceneRect().width(), self.sceneRect().height() / 2 + self.base_point[1])
        self.draw_segment(Segment([Point(x1, y1), Point(x2, y2)], color))

    def draw_function(self, shape):
        for i in range(0, 795, 1):
            x1, y1 = self.to_logical_coords(i, 0)
            x2, y2 = self.to_logical_coords(i+1, 0)
            scene_x1, scene_y1 = self.to_scene_coords(x1, float(shape.evaluate(x1)))
            scene_x, scene_y = self.to_scene_coords(x2, float(shape.evaluate(x2)))
            line = QGraphicsLineItem(scene_x1, scene_y1, scene_x, scene_y)
            line.setPen(QPen(QColor(*shape.color), shape.width))
            self.addItem(line)

    def draw_grid(self):
        # Отрисовка сетки
        self.clear()
        pen = QPen(QColor(80, 80, 80), 0.5)
        step = self.grid_step

        width = self.sceneRect().width()
        height = self.sceneRect().height()

        upper_threshold = 1e6
        lower_threshold = 1e-4

        left_logical = self.to_logical_coords(0, 0)[0]
        right_logical = self.to_logical_coords(width, height)[0]
        top_logical = self.to_logical_coords(0, 0)[1]
        bottom_logical = self.to_logical_coords(width, height)[1]

        def format_label_value(value):
            if math.isclose(value, 0, abs_tol=1e-15):
                return "0"  # Для нуля всегда возвращаем "0"
            elif abs(value) >= upper_threshold or (abs(value) < lower_threshold and value != 0):
                return "{:.1e}".format(value)
            else:
                return str(round(value, 4))  # Округление для обычных чисел

        x = left_logical - (left_logical % step)
        while x <= right_logical:
            x_scene, top_scene = self.to_scene_coords(x, top_logical)
            _, bottom_scene = self.to_scene_coords(x, bottom_logical)
            self.addLine(x_scene, top_scene, x_scene, bottom_scene, pen)
            self.add_grid_label(format_label_value(x), x_scene, top_scene)

            x += step

        y = bottom_logical - (bottom_logical % step)
        while y <= top_logical:
            left_scene, y_scene = self.to_scene_coords(left_logical, y)
            right_scene, _ = self.to_scene_coords(right_logical, y)
            self.addLine(left_scene, y_scene, right_scene, y_scene, pen)
            self.add_grid_label(format_label_value(y), left_scene, y_scene)

            y += step

    def add_grid_label(self, text, pos_x, pos_y, font="Aptos", size=6, color=(70, 68, 81, 200)):
        label = QGraphicsTextItem(str(text))
        font = QFont(font, size)  # Выбираем шрифт для подписей
        label.setFont(font)
        label.setDefaultTextColor(QColor(*color))
        label.setPos(pos_x, pos_y)  # Позиционирование текста
        self.addItem(label)

    def draw_shapes(self):
        # Отрисовка постоянных фигур
        for shape in self.shapes_manager.shapes[Line]:
            self.draw_lines(shape)
        for shape in self.shapes_manager.shapes[Segment]:
            self.draw_segment(shape)
        for shape in self.shapes_manager.shapes[Ray]:
            self.draw_ray(shape)
        for shape in self.shapes_manager.shapes[Circle]:
            self.draw_circle(shape)
        for shape in self.shapes_manager.shapes[Point]:
            self.draw_point(shape)
        for text in self.shapes_manager.shapes[Inf]:
            self.draw_text(text)

    def draw_text(self, text, font="Aptos", size=10, color=(0, 0, 0, 255)):
        label = QGraphicsTextItem(text.message)
        font = QFont(font, size)  # Выбираем шрифт для подписей
        label.setFont(font)
        label.setDefaultTextColor(QColor(*color))
        pos_x, pos_y = self.to_scene_coords(text.x, text.y)
        label.setPos(pos_x, pos_y)  # Позиционирование текста
        self.addItem(label)

    def draw_circle(self, shape):
        scene_x1, scene_y1 = self.to_scene_coords(shape.point_1.x, shape.point_1.y)
        scene_x, scene_y = self.to_scene_coords(shape.point_2.x, shape.point_2.y)
        rad = (((scene_x1 - scene_x) ** 2 + (scene_y1 - scene_y) ** 2) ** 0.5)

        ellipse = QGraphicsEllipseItem(scene_x1 - rad, scene_y1 - rad, 2 * rad, 2 * rad)  # координаты левого верхнего угла, ширина и высота
        ellipse.setPen(QPen(QColor(*shape.color), shape.width))
        ellipse.setBrush(QColor(*shape.color[0:3], 25))
        self.addItem(ellipse)

    def draw_point(self, shape):
        # Отрисовка точек
        radius = shape.radius
        scene_x, scene_y = self.to_scene_coords(shape.x, shape.y)
        ellipse = QGraphicsEllipseItem(scene_x - radius, scene_y - radius, 2 * radius, 2 * radius)
        ellipse.setBrush(QBrush(QColor(*shape.color)))
        self.addItem(ellipse)
        text = Inf(shape.x, shape.y, shape.name)
        self.draw_text(text)

    def draw_segment(self, shape):
        # Отрисовка линий
        scene_x1, scene_y1 = self.to_scene_coords(shape.point_1.x, shape.point_1.y)
        scene_x2, scene_y2 = self.to_scene_coords(shape.point_2.x, shape.point_2.y)
        segment = QGraphicsLineItem(scene_x1, scene_y1, scene_x2, scene_y2)
        segment.setPen(QPen(QColor(*shape.color), shape.width))
        self.addItem(segment)

    def draw_ray(self, shape):
        scene_x1, scene_y1 = self.to_scene_coords(shape.point_1.x, shape.point_1.y)
        scene_x, scene_y = self.to_scene_coords(shape.point_2.x, shape.point_2.y)
        if scene_x1 == scene_x:
            if scene_y > scene_y1:
                line = QGraphicsLineItem(scene_x1, scene_y1, scene_x, self.sceneRect().height())
            else:
                line = QGraphicsLineItem(scene_x1, 0, scene_x, scene_y1)
            line.setPen(QPen(QColor(*shape.color), shape.width))
            self.addItem(line)
        else:
            slope = (shape.point_2.y - shape.point_1.y) / (shape.point_2.x - shape.point_1.x)
            intercept = shape.point_2.y - slope * shape.point_2.x
            x1, y1 = self.to_logical_coords(0, 0)  # координаты верхнего левого угла
            x2, y2 = self.to_logical_coords(self.sceneRect().width(), self.sceneRect().height())
            if scene_x > scene_x1:
                scene_x, scene_y = self.to_scene_coords(x2, slope * (x2) + intercept)
                line = QGraphicsLineItem(scene_x1, scene_y1, scene_x, scene_y)
            else:
                scene_x, scene_y = self.to_scene_coords(x1, slope * (x1) + intercept)
                line = QGraphicsLineItem(scene_x1, scene_y1, scene_x, scene_y)
            line.setPen(QPen(QColor(*shape.color), shape.width))
            self.addItem(line)

    def draw_lines(self, shape):
        scene_x1, scene_y1 = self.to_scene_coords(shape.point_1.x, shape.point_1.y)
        scene_x, scene_y = self.to_scene_coords(shape.point_2.x, shape.point_2.y)
        if scene_x1 == scene_x:
            line = QGraphicsLineItem(scene_x1, 0, scene_x, self.sceneRect().height())
            line.setPen(QPen(QColor(*shape.color), shape.width))
            self.addItem(line)
        else:
            slope = (shape.point_2.y - shape.point_1.y) / (shape.point_2.x - shape.point_1.x)
            intercept = shape.point_2.y - slope * shape.point_2.x
            x1, y1 = self.to_logical_coords(0, 0)  # координаты верхнего левого угла
            x2, y2 = self.to_logical_coords(self.sceneRect().width(), self.sceneRect().height())
            scene_x1, scene_y1 = self.to_scene_coords(x1, slope * (x1) + intercept)
            scene_x, scene_y = self.to_scene_coords(x2, slope * (x2) + intercept)
            line = QGraphicsLineItem(scene_x1, scene_y1, scene_x, scene_y)
            line.setPen(QPen(QColor(*shape.color), shape.width))
            self.addItem(line)

    def draw_temp_shapes(self):
        # Отрисовка временных линий (предпросмотр)
        for shape in self.shapes_manager.temp_segments:
            self.draw_segment(shape)
        for shape in self.shapes_manager.temp_lines:
            self.draw_lines(shape)
        for shape in self.shapes_manager.temp_rays:
            self.draw_ray(shape)
        for shape in self.shapes_manager.temp_circles:
            self.draw_circle(shape)
