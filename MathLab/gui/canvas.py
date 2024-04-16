from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, \
    QGraphicsPathItem
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPainterPath
from PyQt5.QtCore import Qt, QPointF, QLineF
from core.shapes_manager import ShapesManager
from core.geometric_objects.figure import *
from tests.test_distances import *
import math
import time


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

    def update_scene(self):
        self.clear()  # Очищаем
        self.draw_grid()  # Рисуем сетку
        self.draw_coordinate_axes()  # Рисуем оси координат
        self.draw_temp_shapes()  # Рисуем временные фигуры
        self.draw_shapes()  # Рисуем постоянные фигуры

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

    def draw_function(self, shape):
        for i in range(0, 795, 1):
            x1, y1 = self.to_logical_coords(i, 0)
            x2, y2 = self.to_logical_coords(i + 1, 0)
            scene_x1, scene_y1 = self.to_scene_coords(x1, float(shape.evaluate(x1)))
            scene_x, scene_y = self.to_scene_coords(x2, float(shape.evaluate(x2)))
            line = QGraphicsLineItem(scene_x1, scene_y1, scene_x, scene_y)
            line.setPen(QPen(QColor(*shape.color), shape.width))
            self.addItem(line)

    def draw_grid(self, color=(80, 80, 80, 255)):
        # Отрисовка сетки
        self.clear()
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
            elif abs(value) >= upper_threshold or (abs(value) < lower_threshold and value != 0):
                return "{:.1e}".format(value)
            else:
                return str(round(value, 4))  # Округление для обычных чисел

        x = left_logical - (left_logical % step)
        while x <= right_logical:
            x_scene, top_scene = self.to_scene_coords(x, top_logical)
            _, bottom_scene = self.to_scene_coords(x, bottom_logical)
            self.addLine(x_scene, top_scene, x_scene, bottom_scene, pen)

            if self.draw_minor_gridlines:
                for i in range(1, 5):  # Доп. линии
                    thin_x_scene, _ = self.to_scene_coords(x + i * sub_step, 0)
                    self.addLine(thin_x_scene, 0, thin_x_scene, height, thin_pen)

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
            self.addLine(left_scene, y_scene, right_scene, y_scene, pen)

            if self.draw_minor_gridlines:
                for i in range(1, 5):  # Доп. линии
                    _, thin_y_scene = self.to_scene_coords(0, y + i * sub_step)
                    self.addLine(0, thin_y_scene, width, thin_y_scene, thin_pen)

            if not (math.isclose(y, 0, abs_tol=1e-15)):
                self.draw_text(format_label_value(y), label_x_pos, y_scene, size=6, color=(70, 68, 81, 200),
                               center_y=True, pos_adj=True)
            y += step

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
        scene_x1, scene_y1 = self.to_scene_coords(shape.points[0].entity.x, shape.points[0].entity.y)
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
        scene_x1, scene_y1 = self.to_scene_coords(shape.points[0].entity.x, shape.points[0].entity.y)
        scene_x2, scene_y2 = self.to_scene_coords(shape.points[1].entity.x, shape.points[1].entity.y)
        segment = QGraphicsLineItem(scene_x1, scene_y1, scene_x2, scene_y2)
        segment.setPen(QPen(QColor(*shape.color), shape.width))
        self.addItem(segment)

    def draw_ray(self, shape):
        scene_x1, scene_y1 = self.to_scene_coords(shape.points[0].entity.x, shape.points[0].entity.y)
        scene_x, scene_y = self.to_scene_coords(shape.points[1].entity.x, shape.points[1].entity.y)
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
