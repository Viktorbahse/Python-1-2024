from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import Qt
from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import *
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor


class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.current_tool = 'Point'  # Текущий инструмент
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        scene_pos = self.mapToScene(event.pos())  # Мышь в координаты сцены
        logical_pos = self.scene().to_logical_coords(scene_pos.x(), scene_pos.y())  # Сцены в логические(математические) координаты

        print(f"Logical coordinates: {logical_pos}")
        print(f"scene_pos: {scene_pos.x(), scene_pos.y()}")

        if self.current_tool == 'Line' and hasattr(self, 'temp_point'):
            # Если текущий инструмент - линия и начальная точка установлена, рисуем временную линию
            self.scene().shapes_manager.clear_temp_lines()  # Очистка предыдущих временных линий
            self.scene().shapes_manager.add_temp_line(
                Line(self.temp_point[0], self.temp_point[1], logical_pos[0], logical_pos[1], "blue", ))

        self.scene().update_scene()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        scene_pos = self.mapToScene(event.pos())
        logical_pos = self.scene().to_logical_coords(scene_pos.x(), scene_pos.y())

        if self.current_tool == 'Line':
            self.scene().shapes_manager.add_shape(Point(logical_pos[0], logical_pos[1]))
            if not hasattr(self, 'temp_point'):
                self.temp_point = logical_pos  # Устанавливаем начальные точки линии (первое нажатие)
            else:
                # Завершаем рисовать линию и добавлям её в список постоянных фигур (второе нажатие)
                self.scene().shapes_manager.clear_temp_lines()
                final_point = logical_pos
                self.scene().shapes_manager.add_shape(
                    Line(self.temp_point[0], self.temp_point[1], final_point[0], final_point[1]))
                del self.temp_point
        else:
            # Добавление и удаление точки
            if event.button() == Qt.LeftButton:
                self.scene().shapes_manager.add_shape(Point(logical_pos[0], logical_pos[1]))
            elif event.button() == Qt.RightButton:
                shape = self.scene().shapes_manager.find_shape(logical_pos[0], logical_pos[1])
                if shape:
                    self.scene().shapes_manager.remove_shape(shape)

        self.scene().update_scene()

    def keyPressEvent(self, event):
        step = 10
        # Перемещение, зум, переключение инструментов
        if event.key() == Qt.Key_Equal:
            self.scene().zoom_factor *= 1.1
        if event.key() == Qt.Key_Minus:
            self.scene().zoom_factor /= 1.1
            self.scene().draw_grid()
        if event.key() == Qt.Key_W:
            self.scene().base_point[1] -= step
        elif event.key() == Qt.Key_S:
            self.scene().base_point[1] += step
        elif event.key() == Qt.Key_A:
            self.scene().base_point[0] -= step
        elif event.key() == Qt.Key_D:
            self.scene().base_point[0] += step
        elif event.key() == Qt.Key_Q:
            self.current_tool = 'Line' if self.current_tool == 'Point' else 'Point'

        self.scene().update_scene()
        super().keyPressEvent(event)
