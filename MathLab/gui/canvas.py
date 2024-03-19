from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
from PyQt5.QtCore import Qt
from core.shapes_manager import ShapesManager
from core.geometric_objects.figure import *


class Canvas(QGraphicsScene):
    def __init__(self, parent=None, zoom_factor=1.0):
        super().__init__(parent)

        self.shapes_manager = ShapesManager()
        self.zoom_factor = zoom_factor
        self.grid_step = 50
        self.base_point = [0, 0]
        self.setSceneRect(0, 0, 800 - 2, 600 - 2)
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
        self.draw_grid()

    def update_scene(self):
        self.clear()  # Очищаем
        self.draw_grid()  # Рисуем сетку
        self.draw_coordinate_axes()  # Рисуем оси координат
        self.draw_temp_line()  # Рисуем временные фигуры (пока только линии)
        self.draw_shapes()  # Рисуем постоянные фигуры

    def draw_coordinate_axes(self):
        center_x = self.sceneRect().width() / 2 + self.base_point[0]
        center_y = self.sceneRect().height() / 2 + self.base_point[1]
        self.addLine(center_x, 0, center_x, self.sceneRect().height(), QPen(Qt.black, 1))
        self.addLine(0, center_y, self.sceneRect().width(), center_y, QPen(Qt.black, 1))

    def draw_grid(self):
        # Отрисовка сетки
        self.clear()
        pen = QPen(Qt.gray, 0.5)
        step = self.grid_step

        width = self.sceneRect().width()
        height = self.sceneRect().height()

        left_logical = self.to_logical_coords(0, 0)[0]
        right_logical = self.to_logical_coords(width, height)[0]
        top_logical = self.to_logical_coords(0, 0)[1]
        bottom_logical = self.to_logical_coords(width, height)[1]

        x = left_logical - (left_logical % step)
        while x <= right_logical:
            x_scene, top_scene = self.to_scene_coords(x, top_logical)
            _, bottom_scene = self.to_scene_coords(x, bottom_logical)
            self.addLine(x_scene, top_scene, x_scene, bottom_scene, pen)
            x += step

        y = bottom_logical - (bottom_logical % step)
        while y <= top_logical:
            left_scene, y_scene = self.to_scene_coords(left_logical, y)
            right_scene, _ = self.to_scene_coords(right_logical, y)
            self.addLine(left_scene, y_scene, right_scene, y_scene, pen)
            y += step

    def draw_shapes(self):
        # Отрисовка постоянных фигур
        for shape in self.shapes_manager.shapes[Segment]:
            self.draw_segment(shape)
            # self.draw_inf_lines(shape)
        for shape in self.shapes_manager.shapes[Point]:
            self.draw_point(shape)

    def draw_point(self, shape):
        # Отрисовка точек
        radius = shape.radius
        scene_x, scene_y = self.to_scene_coords(shape.x, shape.y)
        ellipse = QGraphicsEllipseItem(scene_x - radius, scene_y - radius, 2 * radius, 2 * radius)
        ellipse.setBrush(QBrush(QColor(*shape.color)))
        self.addItem(ellipse)

    def draw_segment(self, shape):
        # Отрисовка линий
        scene_x1, scene_y1 = self.to_scene_coords(shape.point_1.x, shape.point_1.y)
        scene_x2, scene_y2 = self.to_scene_coords(shape.point_2.x, shape.point_2.y)
        segment = QGraphicsLineItem(scene_x1, scene_y1, scene_x2, scene_y2)
        segment.setPen(QPen(QColor(*shape.color), shape.width))
        self.addItem(segment)

    def draw_inf_lines(self, shape):
        scene_x1, scene_y1 = self.to_scene_coords(shape.line.p1.x, shape.line.p1.y)
        scene_x, scene_y = self.to_scene_coords(shape.line.p2.x, shape.line.p2.y)
        if scene_x1 == scene_x:
            line = QGraphicsLineItem(scene_x1, 0, scene_x, self.sceneRect().height())
            line.setPen(QPen(QColor(*shape.color), shape.width))
            self.addItem(line)
        elif scene_y1 == scene_y:
            line = QGraphicsLineItem(0, scene_y1, self.sceneRect().width(), scene_y)
            line.setPen(QPen(QColor(*shape.color), shape.width))
            self.addItem(line)
        else:
            slope = (shape.line.p2.y - shape.line.p1.y) / (shape.line.p2.x - shape.line.p1.x)
            intercept = shape.line.p2.y - slope * shape.line.p2.x
            x1, y1 = self.to_logical_coords(0, 0)  # координаты верхнего левого угла
            x2, y2 = self.to_logical_coords(self.sceneRect().width(), self.sceneRect().height())
            scene_x1, scene_y1 = self.to_scene_coords(x1, slope * (x1) + intercept)
            scene_x, scene_y = self.to_scene_coords(x2, slope * (x2) + intercept)
            line = QGraphicsLineItem(scene_x1, scene_y1, scene_x, scene_y)
            line.setPen(QPen(QColor(*shape.color), shape.width))
            self.addItem(line)

    def draw_temp_line(self):
        # Отрисовка временных линий (предпросмотр)
        for shape in self.shapes_manager.temp_items:
            self.draw_segment(shape)
