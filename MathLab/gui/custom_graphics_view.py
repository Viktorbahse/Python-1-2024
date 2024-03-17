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
        self.setRenderHint(QPainter.Antialiasing)  # Включение антиалиасинга (будет плавность)
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
                Line(Point(self.temp_point[0], self.temp_point[1]), Point(logical_pos[0], logical_pos[1]), (37, 109, 133, 255)))
        elif self.current_tool == 'Polygon' and hasattr(self, 'polygon_points') and self.polygon_points:
            last_point = self.polygon_points[-1]

            # Очищаем предыдущие временные линии
            self.scene().shapes_manager.clear_temp_lines()
            # Добавляем временную линию для предпросмотра
            self.scene().shapes_manager.add_temp_line(Line(last_point, Point(logical_pos[0], logical_pos[1]), (37, 109, 133, 255)))

        self.scene().update_scene()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        scene_pos = self.mapToScene(event.pos())
        logical_pos = self.scene().to_logical_coords(scene_pos.x(), scene_pos.y())

        closest_point = self.scene().shapes_manager.find_closest_point(logical_pos[0], logical_pos[1], 10 / self.scene().zoom_factor)  # Ближайшие точки
        if self.current_tool == 'Line':
            if not hasattr(self, 'temp_point'):
                # Устанавливаем начальные точки линии (первое нажатие)
                if closest_point:  # Если нашли ближайшую точку, используем её как начало линии
                    self.temp_point = (closest_point.point.x, closest_point.point.y)
                else:  # Иначе устанавливаем текущую позицию
                    self.temp_point = logical_pos
                    self.scene().shapes_manager.add_shape(Point(logical_pos[0], logical_pos[1]))
            else:
                # Завершаем рисовать линию и добавлям её в список постоянных фигур (второе нажатие)
                if closest_point:
                    final_point = (closest_point.point.x, closest_point.point.y)
                else:
                    final_point = logical_pos
                    self.scene().shapes_manager.add_shape(Point(logical_pos[0], logical_pos[1]))
                self.scene().shapes_manager.clear_temp_lines()
                self.scene().shapes_manager.add_shape(
                    Line(Point(self.temp_point[0], self.temp_point[1]), Point(final_point[0], final_point[1])))
                del self.temp_point
        elif self.current_tool == 'Polygon':
            if not hasattr(self, 'polygon_points'):
                self.current_polygon = Polygon([])
                self.polygon_points = []

            # Если ближайшая точка найдена и это начальная точка многоугольника, то завершаем рисование
            if closest_point and self.polygon_points and closest_point == self.polygon_points[0]:
                if len(self.polygon_points) > 1:  # Создаем линию от последней точки к первой
                    last_point = self.polygon_points[-1]
                    self.scene().shapes_manager.add_shape(Line(last_point, closest_point, owner=[self.current_polygon]))
                self.scene().shapes_manager.clear_temp_lines()
                self.scene().shapes_manager.add_shape(self.current_polygon)
                delattr(self, 'polygon_points')
            else:
                if closest_point:
                    new_point = closest_point
                    new_point.add_to_owner(self.current_polygon)
                else:
                    new_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_polygon])
                    self.scene().shapes_manager.add_shape(new_point)
                if not self.polygon_points or (self.polygon_points and new_point != self.polygon_points[-1]):
                    if self.polygon_points:
                        last_point = self.polygon_points[-1]
                        self.scene().shapes_manager.add_shape(Line(last_point, new_point, owner=[self.current_polygon]))
                    self.polygon_points.append(new_point)
                    self.current_polygon.add_point(new_point)

            self.scene().shapes_manager.clear_temp_lines()
        else:
            # Добавление и удаление точки
            if event.button() == Qt.LeftButton:
                if not closest_point:  # добавляем новую, если точка в радиусе не найдена
                    self.scene().shapes_manager.add_shape(Point(logical_pos[0], logical_pos[1]))
            elif event.button() == Qt.RightButton:
                shape = self.scene().shapes_manager.find_shape(logical_pos[0], logical_pos[1], 10 / self.scene().zoom_factor)
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
            self.scene().base_point[1] += step
        elif event.key() == Qt.Key_S:
            self.scene().base_point[1] -= step
        elif event.key() == Qt.Key_A:
            self.scene().base_point[0] += step
        elif event.key() == Qt.Key_D:
            self.scene().base_point[0] -= step
        elif event.key() == Qt.Key_Q:
            if self.current_tool == 'Point':
                self.current_tool = 'Line'
            elif self.current_tool == 'Line':
                self.current_tool = 'Polygon'
            else:
                self.current_tool = 'Point'

        self.scene().update_scene()
        super().keyPressEvent(event)
