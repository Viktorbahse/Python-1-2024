from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsPathItem
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath
from PyQt5.QtCore import Qt, QPointF, QLineF, QThread, pyqtSignal, QTimer, QObject
from core.shapes_manager import ShapesManager
from core.geometric_objects.figure import *
from tests.test_distances import *
from tests.timing import *
import numpy as np
import sympy as sp
import math
import time
import multiprocessing
import numpy as np
import sympy as sp
import concurrent.futures


class Canvas(QGraphicsScene):
    def __init__(self, width, height, parent=None, zoom_factor=65.0):
        super().__init__(parent)
        self.setSceneRect(0, 0, width, height)

        self.shapes_manager = ShapesManager()
        self.zoom_factor = zoom_factor
        self.grid_step = 1
        self.base_point = [0, 0]

        self.draw_minor_gridlines = True  # Включает отрисовку мелкой сетки

        self.canvas_logical_width = abs(self.to_logical_coords(0, 0)[0] -
                                        self.to_logical_coords(self.sceneRect().width(), self.sceneRect().height())[0])
        self.lower_width = self.canvas_logical_width / 2
        self.upper_width = self.canvas_logical_width * 2

        self.grid_path = QPainterPath()  # Наша сетка, представленная одним путем (для оптимизации)
        self.thin_grid_path = QPainterPath()  # Мелкая сетка, представленная одним путем

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

    def set_zoom_factor(self, factor, cursor_scene_pos=None):
        #  Место, где находится курсор, остается неподвижным. Если курсор вне холста, то делает приближение к центру
        if cursor_scene_pos is None:
            cursor_scene_pos = QPointF(self.sceneRect().width() / 2, self.sceneRect().height() / 2)
        old_logical_coords = self.to_logical_coords(cursor_scene_pos.x(), cursor_scene_pos.y())
        self.zoom_factor = factor
        new_logical_coords = self.to_logical_coords(cursor_scene_pos.x(), cursor_scene_pos.y())

        delta_x = old_logical_coords[0] - new_logical_coords[0]
        delta_y = new_logical_coords[1] - old_logical_coords[1]

        delta_scene_coords = self.to_scene_coords(delta_x, delta_y)
        center = self.to_scene_coords(0, 0)

        self.base_point[0] -= (delta_scene_coords[0] - center[0])
        self.base_point[1] += (delta_scene_coords[1] - center[1])
        self.grid_step_setting()

    def grid_step_setting(self):  # настройка шага сетки
        current_width = abs(self.to_logical_coords(0, 0)[0] -
                            self.to_logical_coords(self.sceneRect().width(), self.sceneRect().height())[0])

        # Проверяем, нужно ли обновить шаг сетки
        if current_width <= self.lower_width:
            # Уменьшаем шаг сетки и обновляем пороги
            self.grid_step /= 2
            self.upper_width = self.lower_width
            self.lower_width /= 2
        elif current_width >= self.upper_width:
            # Увеличиваем шаг сетки и обновляем пороги
            self.grid_step *= 2
            self.lower_width = self.upper_width
            self.upper_width *= 2

        self.canvas_logical_width = current_width

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

    # @timeit
    def clear_scene(self):
        # Очищает все элементы сцены
        self.clear()
        self.grid_path.clear()  # Сброс основного пути сетки
        self.thin_grid_path.clear()  # Сброс пути мелкой сетки

    @timeit
    def update_scene(self):
        self.clear_scene()  # Очищаем
        self.draw_grid()  # Рисуем сетку
        self.draw_coordinate_axes()  # Рисуем оси координат
        self.draw_temp_shapes()  # Рисуем временные фигуры
        self.draw_shapes()  # Рисуем постоянные фигуры

    def draw_shapes(self):
        # Отрисовка постоянных фигур
        for shape in self.shapes_manager.shapes[Line]:
            if not shape.invisible:
                self.draw_lines(shape)
        for shape in self.shapes_manager.shapes[Segment]:
            if not shape.invisible:
                self.draw_segment(shape)
        for shape in self.shapes_manager.shapes[Ray]:
            if not shape.invisible:
                self.draw_ray(shape)
        for shape in self.shapes_manager.shapes[Circle]:
            if not shape.invisible:
                self.draw_circle(shape)
        self.draw_all_fanctions()
        for shape in self.shapes_manager.shapes[Point]:
            if not shape.invisible:
                self.draw_point(shape)
        for text in self.shapes_manager.shapes[Info]:
            self.draw_text(text.message, *self.to_scene_coords(text.x, text.y), center_x=True, center_y=True)

    def draw_temp_shapes(self):
        # Отрисовка временных линий (предпросмотр)
        for shape in self.shapes_manager.temp_shapes[Segment]:
            self.draw_segment(shape)
        for shape in self.shapes_manager.temp_shapes[Line]:
            self.draw_lines(shape)
        for shape in self.shapes_manager.temp_shapes[Ray]:
            self.draw_ray(shape)
        for shape in self.shapes_manager.temp_shapes[Circle]:
            self.draw_circle(shape)

    def draw_coordinate_axes(self, color=(0, 0, 0, 255)):
        center_x = self.sceneRect().width() / 2 + self.base_point[0]
        center_y = self.sceneRect().height() / 2 + self.base_point[1]
        width = self.sceneRect().width()
        height = self.sceneRect().height()

        # Рисуем оси
        # Пыталась использовать уже написанный метод, но как и draw_segment функция работала очень долго
        self.addLine(center_x, 0, center_x, height, QPen(QColor(*color), 1))
        self.addLine(0, center_y, width, center_y, QPen(QColor(*color), 1))

        arrow_length = 10  # длина стрелочки

        # Стрелочки для x
        self.addLine(width - arrow_length - 2, center_y,
                     width - 2 * arrow_length - 2, center_y + arrow_length / 2, QPen(QColor(*color), 1))
        self.addLine(width - arrow_length - 2, center_y,
                     width - 2 * arrow_length - 2, center_y - arrow_length / 2, QPen(QColor(*color), 1))

        # Стрелочки для y
        self.addLine(center_x, 0, center_x - arrow_length / 2, arrow_length, QPen(QColor(*color), 1))
        self.addLine(center_x, 0, center_x + arrow_length / 2, arrow_length, QPen(QColor(*color), 1))

    def draw_all_fanctions(self):
        path = QPainterPath()
        x_start, _ = self.to_logical_coords(0, 0)
        x_end, _ = self.to_logical_coords(self.sceneRect().width(), 0)
        for func in self.shapes_manager.functions:
            if func.correct:
                bad_points = list(func.discontinuity_points.intersect(sp.Interval(x_start, x_end)))
                if func.type in ["line", "const"]:  # Оптимизация для линий.
                    x, y = x_start, func.evaluate(x_start)
                    if x is not None and y is not None:
                        x, y = self.to_scene_coords(x, y)
                        path.moveTo(QPointF(x, y))
                        x, y = self.to_scene_coords(x_end, func.evaluate(x_end))
                        path.lineTo(QPointF(x, y))
                elif len(bad_points) == 0:
                    drawing_status = False
                    x_values = np.linspace(float(x_start), float(x_end), 1600)
                    y_values = func.f(x_values)
                    for i in range(len(x_values)):
                        if math.isnan(y_values[i]):
                            drawing_status = False
                        else:
                            if not drawing_status:
                                x, y = self.to_scene_coords(x_values[i], y_values[i])
                                path.moveTo(QPointF(x, y))
                                drawing_status = True
                            else:
                                x, y = self.to_scene_coords(x_values[i], y_values[i])
                                path.lineTo(QPointF(x, y))
                else:
                    bad_points = [x_start] + bad_points + [x_end]
                    for i in range(len(bad_points) - 1):
                        if func.is_defined((bad_points[i] + bad_points[i + 1]) / 2):
                            accuracy = 100
                            if len(bad_points) > 5:
                                accuracy = 40
                            x_values = np.linspace(float(bad_points[i] + (bad_points[i + 1] - bad_points[i]) / 200000),
                                                   float(bad_points[i + 1] - (
                                                           bad_points[i + 1] - bad_points[i]) / 200000), accuracy)
                            y_values = func.f(x_values)

                            x, y = self.to_scene_coords(x_values[0], y_values[0])
                            path.moveTo(QPointF(x, y))
                            for j in range(1, len(x_values)):
                                x, y = self.to_scene_coords(x_values[j], y_values[j])
                                path.lineTo(QPointF(x, y))

        path_item = QGraphicsPathItem()
        path_item.setPath(path)
        path_item.setPen(QPen(Qt.red, 2))
        self.addItem(path_item)

    def draw_grid(self, color=(80, 80, 80, 255)):
        # Отрисовка сетки
        pen = QPen(QColor(*color), 0.5)
        thin_pen = QPen(QColor(*color), 0.1)  # Для дополнительных линий между основными
        step = self.grid_step
        sub_step = step / 5

        width = self.sceneRect().width()
        height = self.sceneRect().height()

        upper_threshold = 1e6
        lower_threshold = 1e-4

        left_logical = self.to_logical_coords(0, 0)[0]
        right_logical = self.to_logical_coords(width, height)[0]
        top_logical = self.to_logical_coords(0, 0)[1]
        bottom_logical = self.to_logical_coords(width, height)[1]

        center_x_scene, center_y_scene = self.to_scene_coords(0, 0)
        # Определяем позиции по x
        if center_x_scene > width:
            label_x_pos = width
        elif center_x_scene < 0:
            label_x_pos = 0
        else:
            label_x_pos = center_x_scene

        # Определяем позиции по y
        if center_y_scene > height:
            label_y_pos = height - 55
        elif center_y_scene < 0:
            label_y_pos = 0
        else:
            label_y_pos = center_y_scene

        def format_label_value(value):
            if math.isclose(value, 0, abs_tol=1e-15):
                return "0"  # Для нуля всегда возвращаем "0"
            elif abs(value) >= upper_threshold or int(value) == 0:
                return "{:.1e}".format(value)
            elif abs(value - int(value)) < lower_threshold and (value - int(value)) != 0:
                int_part = int(value)
                fractional_part = value - int_part
                fractional_str = "{:.1e}".format(fractional_part)
                return "{} + {}".format(int_part, fractional_str)
            else:
                return str(round(value, 4))  # Округление для обычных чисел

        x = left_logical - (left_logical % step)
        while x <= right_logical:
            x_scene, top_scene = self.to_scene_coords(x, top_logical)
            _, bottom_scene = self.to_scene_coords(x, bottom_logical)

            self.grid_path.moveTo(x_scene, top_scene)
            self.grid_path.lineTo(x_scene, bottom_scene)

            if self.draw_minor_gridlines:
                for i in range(1, 5):  # Доп. линии
                    thin_x_scene, _ = self.to_scene_coords(x + i * sub_step, 0)

                    self.thin_grid_path.moveTo(thin_x_scene, 0)
                    self.thin_grid_path.lineTo(thin_x_scene, height)

            if not (math.isclose(x, 0, abs_tol=1e-15)):
                self.draw_text(format_label_value(x), x_scene, label_y_pos, size=6, color=(70, 68, 81, 200),
                               center_x=True, pos_adj=True)
            else:
                self.draw_text(format_label_value(x), x_scene, label_y_pos, size=6, color=(70, 68, 81, 200))

            x += step

        y = bottom_logical - (bottom_logical % step)
        while y <= top_logical:
            left_scene, y_scene = self.to_scene_coords(left_logical, y)
            right_scene, _ = self.to_scene_coords(right_logical, y)

            self.grid_path.moveTo(left_scene, y_scene)
            self.grid_path.lineTo(right_scene, y_scene)

            if self.draw_minor_gridlines:
                for i in range(1, 5):  # Доп. линии
                    _, thin_y_scene = self.to_scene_coords(0, y + i * sub_step)

                    self.thin_grid_path.moveTo(0, thin_y_scene)
                    self.thin_grid_path.lineTo(width, thin_y_scene)

            if not (math.isclose(y, 0, abs_tol=1e-15)):
                self.draw_text(format_label_value(y), label_x_pos, y_scene, size=6, color=(70, 68, 81, 200),
                               center_y=True, pos_adj=True)
            y += step

        self.addPath(self.grid_path, pen)
        if self.draw_minor_gridlines:
            self.addPath(self.thin_grid_path, thin_pen)

    def draw_text(self, text, pos_x, pos_y, font="Aptos", size=10, color=(0, 0, 0, 255), center_x=False,
                  center_y=False, pos_adj=False):
        label = QGraphicsTextItem(str(text))
        font = QFont(font, size)  # Выбираем шрифт для подписей
        label.setFont(font)
        label.setDefaultTextColor(QColor(*color))

        rect = label.boundingRect()

        x_bias = rect.width() / 2 if center_x else 0  # Смещение по х, если мы хотим, чтобы оно было в середине
        y_bias = rect.height() / 2 if center_y else 0  # Аналогично
        label.setPos(pos_x - x_bias, pos_y - y_bias)  # Позиционирование текста
        rect = label.boundingRect()

        # Корректировка позиции, если текст выходит за правую или нижнюю границу
        if pos_adj:
            scene_width = self.sceneRect().width()
            scene_height = self.sceneRect().height()
            if label.x() + rect.width() > scene_width:
                # Корректируем, если текст выходит за правую границу
                label.setPos(scene_width - 1.5 * rect.width(), label.y())
            if label.y() + rect.height() >= scene_height:
                label.setPos(scene_height, pos_y - rect.height())  # Корректируем, если текст выходит за нижнюю границу

        self.addItem(label)
        return label

    def draw_circle(self, shape):
        scene_x1, scene_y1 = self.to_scene_coords(shape.entity.center.x, shape.entity.center.y)
        scene_x, scene_y = self.to_scene_coords(shape.points[1].entity.x, shape.points[1].entity.y)
        rad = (((scene_x1 - scene_x) ** 2 + (scene_y1 - scene_y) ** 2) ** 0.5)

        # координаты левого верхнего угла, ширина и высота
        ellipse = QGraphicsEllipseItem(scene_x1 - rad, scene_y1 - rad, 2 * rad, 2 * rad)
        ellipse.setPen(QPen(QColor(*shape.color), shape.width))
        ellipse.setBrush(QColor(*shape.color[0:3], 25))
        self.addItem(ellipse)

    def draw_point(self, shape):
        # Отрисовка точек
        radius = shape.radius
        scene_x, scene_y = self.to_scene_coords(shape.entity.x, shape.entity.y)
        ellipse = QGraphicsEllipseItem(scene_x - radius, scene_y - radius, 2 * radius, 2 * radius)
        ellipse.setBrush(QBrush(QColor(*shape.color)))
        self.addItem(ellipse)
        self.draw_text(shape.name, *self.to_scene_coords(shape.entity.x, shape.entity.y))

    def draw_segment(self, shape):
        # Отрисовка линий
        scene_x1, scene_y1 = self.to_scene_coords(shape.entity.p1.x, shape.entity.p1.y)
        scene_x2, scene_y2 = self.to_scene_coords(shape.entity.p2.x, shape.entity.p2.y)
        segment = QGraphicsLineItem(scene_x1, scene_y1, scene_x2, scene_y2)
        segment.setPen(QPen(QColor(*shape.color), shape.width))
        self.addItem(segment)

    def draw_ray(self, shape):
        scene_x1, scene_y1 = self.to_scene_coords(shape.entity.p1.x, shape.entity.p1.y)
        scene_x, scene_y = self.to_scene_coords(shape.entity.p2.x, shape.entity.p2.y)
        if scene_x1 == scene_x:
            if scene_y > scene_y1:
                line = QGraphicsLineItem(scene_x1, scene_y1, scene_x, self.sceneRect().height())
            else:
                line = QGraphicsLineItem(scene_x1, 0, scene_x, scene_y1)
            line.setPen(QPen(QColor(*shape.color), shape.width))
            self.addItem(line)
        else:
            slope = shape.entity.slope
            intercept = shape.entity.p2.y - slope * shape.entity.p2.x
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
        scene_x1, scene_y1 = self.to_scene_coords(shape.entity.p1.x, shape.entity.p1.y)
        scene_x, scene_y = self.to_scene_coords(shape.entity.p2.x, shape.entity.p2.y)
        if scene_x1 == scene_x:
            line = QGraphicsLineItem(scene_x1, 0, scene_x, self.sceneRect().height())
            line.setPen(QPen(QColor(*shape.color), shape.width))
            self.addItem(line)
        else:
            slope = shape.entity.slope
            intercept = shape.entity.p2.y - slope * shape.entity.p2.x
            x1, y1 = self.to_logical_coords(0, 0)  # координаты верхнего левого угла
            x2, y2 = self.to_logical_coords(self.sceneRect().width(), self.sceneRect().height())
            scene_x1, scene_y1 = self.to_scene_coords(x1, slope * (x1) + intercept)
            scene_x, scene_y = self.to_scene_coords(x2, slope * (x2) + intercept)
            line = QGraphicsLineItem(scene_x1, scene_y1, scene_x, scene_y)
            line.setPen(QPen(QColor(*shape.color), shape.width))
            self.addItem(line)

    def add_arrow_head(self, shape):
        # Рисует стрелочку для вектора
        scene_x1, scene_y1 = self.to_scene_coords(shape.point_1.x, shape.point_1.y)
        scene_x2, scene_y2 = self.to_scene_coords(shape.point_2.x, shape.point_2.y)

        # Рассчитываем направления стрелки
        dx = scene_x2 - scene_x1
        dy = scene_y2 - scene_y1
        angle = math.atan2(dy, dx)

        arrow_length = 17  # Длина стрелки
        angle_bisector = math.pi / 12  # Угол

        # Создаем путь для стрелки
        arrow_path = QPainterPath()
        arrow_tip = QPointF(scene_x2, scene_y2)
        arrow_path.moveTo(arrow_tip.x(), arrow_tip.y())

        # Вычисляем точки для "крыльев"
        left_wing = arrow_tip - QPointF(arrow_length * math.cos(angle + angle_bisector),
                                        arrow_length * math.sin(angle + angle_bisector))
        right_wing = arrow_tip - QPointF(arrow_length * math.cos(angle - angle_bisector),
                                         arrow_length * math.sin(angle - angle_bisector))

        # Рисуем "крылья"
        arrow_path.lineTo(left_wing)
        arrow_path.lineTo(right_wing)
        arrow_path.closeSubpath()

        arrow_item = QGraphicsPathItem(arrow_path)
        arrow_item.setPen(QPen(QColor(*shape.color), shape.width))
        arrow_item.setBrush(QColor(*shape.color[:-1], 255))  # Заливка стрелки
        self.addItem(arrow_item)
