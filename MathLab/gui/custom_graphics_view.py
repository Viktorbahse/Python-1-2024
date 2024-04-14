from PyQt5.QtWidgets import QGraphicsView, QShortcut
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import *
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor


class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.max_zoom_factor = 1e+16
        self.min_zoom_factor = 1e-11
        self.zoom_multiplier = 1.08  # Если установить меньше ~1.08, то сетка в самом близком приближении становиться очень мелкой

        self.startMove = False
        self.current_tool = 'Move'  # Текущий инструмент
        self.polygon_points = None  # Список точек для текущего рисуемого многоугольника.
        self.temp_point = None  # Временная точка для начала сегмента.
        self.temp_line = None
        self.grid_gravity_mode = True

        # Связывает название инструмента для рисования с методом, который будет вызван при нажатии на мышку при этом инструменте
        self.drawing_tools = {
            'Point': self.handle_point_creation,
            'Segment': self.handle_segment_creation,
            'Polygon': self.handle_polygon_creation,
            'Line': self.handle_line_creation,
            'Ray': self.handle_ray_creation,
            'Circle': self.handle_circle_creation,
            'Parallel_Line': self.handle_parallel_line_creation,
            'Perpendicular_Line': self.handle_perpendicular_line_creation
        }

        self.setRenderHint(QPainter.Antialiasing)  # Включение сглаживания
        self.setMouseTracking(True)

    def initiate_temp_shape_drawing(self, logical_pos):
        # Инициирует отрисовку временной фигуры (добавляет временную фигуру в shapes_manager)
        temp_color = (37, 109, 133, 200)
        temp_shape = None

        if self.temp_line is not None and self.current_tool in ['Parallel_Line', 'Perpendicular_Line']:
            self.draw_temp_parallel_line(sp.Point(logical_pos[0], logical_pos[1]))
        elif self.temp_point is not None:
            if self.current_tool == 'Segment':
                temp_shape = Segment([self.temp_point, Point(logical_pos[0], logical_pos[1])], color=temp_color)
            elif self.current_tool == 'Line':
                temp_shape = Line([self.temp_point, Point(logical_pos[0], logical_pos[1])], color=temp_color)
            elif self.current_tool == 'Ray':
                temp_shape = Ray([self.temp_point, Point(logical_pos[0], logical_pos[1])], color=temp_color)
            elif self.current_tool == 'Circle':
                temp_shape = Circle([self.temp_point, Point(logical_pos[0], logical_pos[1])], color=temp_color)
        elif self.current_tool == 'Polygon' and self.polygon_points:
            temp_shape = Segment([self.polygon_points[-1], Point(logical_pos[0], logical_pos[1])], color=temp_color)

        if temp_shape:
            self.scene().shapes_manager.clear_temp_shapes(type(temp_shape))
            self.scene().shapes_manager.add_temp_shape(temp_shape)

    def draw_temp_parallel_line(self, point, color=(37, 109, 133, 200)):
        # Добавляет временную линию в shapes_manager для отрисовки. Принимает точки класса Point.
        self.scene().shapes_manager.clear_temp_shapes()
        line = Line()
        line.line = self.temp_line.parallel_line(point)
        self.scene().shapes_manager.add_temp_shape(line)

    def handle_move_canvas(self, scene_pos):
        self.startMove = True
        self.startMovePoint = scene_pos
        self.saveBasePointX = self.scene().base_point[0]
        self.saveBasePointY = self.scene().base_point[1]

    def handle_point_creation(self, logical_pos=None, point=None, closest_point=False):
        # Добавляет точку на сцену
        if not closest_point:  # Добавляет новую только тогда, когда не найдена точка в ближайшем радиусе
            if logical_pos is not None:
                point = Point(logical_pos[0], logical_pos[1])
            self.scene().shapes_manager.add_shape(point)

    def handle_perpendicular_line_creation(self, logical_pos, closest_point, closest_line):
        if self.temp_line is None and self.temp_point is None:
            self.current_line = Line()  # Создаем пустую линию.
            if closest_line is not None:
                self.temp_line = closest_line.perpendicular_line(sp.Point(logical_pos[0], logical_pos[1]))
            else:
                if closest_point:  # Если рядом с курсором нашлась точка, то устанавливаем ее как начальную.
                    closest_point.add_to_owner(owner=self.current_line)
                    self.temp_point = closest_point
                else:  # Если не нашлась, то устанавливаем начальную точку по координатам курсора.
                    self.temp_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_line])
                    self.handle_point_creation(point=self.temp_point)
                self.current_line.add_point(self.temp_point)
        elif self.temp_line is not None and self.temp_point is None:
            if closest_point:
                closest_point.add_to_owner(owner=self.current_line)
                final_point = closest_point
            else:
                final_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_line])
                self.handle_point_creation(point=final_point)
            self.current_line.add_point(final_point)
            self.current_line.line = self.temp_line.parallel_line(sp.Point(final_point.x, final_point.y))
            self.scene().shapes_manager.clear_temp_shapes()
            self.scene().shapes_manager.add_shape(self.current_line)
            self.temp_point = None
            self.temp_line = None
        elif self.temp_line is None and self.temp_point is not None:
            if closest_line is not None:
                self.temp_line = closest_line
                self.current_line.line = self.temp_line.perpendicular_line(
                    sp.Point(self.temp_point.x, self.temp_point.y))
                self.scene().shapes_manager.clear_temp_shapes()
                self.scene().shapes_manager.add_shape(self.current_line)
                self.temp_point = None
                self.temp_line = None

    def handle_parallel_line_creation(self, logical_pos, closest_point, closest_line):
        if self.temp_line is None and self.temp_point is None:
            self.current_line = Line()  # Создаем пустую линию.
            if closest_line is not None:
                self.temp_line = closest_line
            else:
                if closest_point:  # Если рядом с курсором нашлась точка, то устанавливаем ее как начальную.
                    closest_point.add_to_owner(owner=self.current_line)
                    self.temp_point = closest_point
                else:  # Если не нашлась, то устанавливаем начальную точку по координатам курсора.
                    self.temp_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_line])
                    self.handle_point_creation(point=self.temp_point)
                self.current_line.add_point(self.temp_point)
        elif self.temp_line is not None and self.temp_point is None:
            if closest_point:
                closest_point.add_to_owner(owner=self.current_line)
                final_point = closest_point
            else:
                final_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_line])
                self.handle_point_creation(point=final_point)
            self.current_line.add_point(final_point)
            self.current_line.line = self.temp_line.parallel_line(sp.Point(final_point.x, final_point.y))
            self.scene().shapes_manager.clear_temp_shapes()
            self.scene().shapes_manager.add_shape(self.current_line)
            self.temp_point = None
            self.temp_line = None
        elif self.temp_line is None and self.temp_point is not None:
            if closest_line is not None:
                self.temp_line = closest_line
                self.current_line.line = self.temp_line.parallel_line(sp.Point(self.temp_point.x, self.temp_point.y))
                self.scene().shapes_manager.clear_temp_shapes()
                self.scene().shapes_manager.add_shape(self.current_line)
                self.temp_point = None
                self.temp_line = None

    def handle_line_creation(self, logical_pos, closest_point):
        if self.temp_point is None:  # Выбираем начальную точку линии.
            self.current_line = Line()  # Создаем пустую линию.
            if closest_point:  # Если рядом с курсором нашлась точка, то устанавливаем ее как начальную.
                closest_point.add_to_owner(owner=self.current_line)
                self.temp_point = closest_point
            else:  # Если не нашлась, то устанавливаем начальную точку по координатам курсора.
                self.temp_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_line])
                self.handle_point_creation(point=self.temp_point)
            self.current_line.add_point(self.temp_point)
        else:
            # Завершаем рисовать линию и добавляем её в список постоянных фигур (второе нажатие)
            if closest_point:
                closest_point.add_to_owner(owner=self.current_line)
                final_point = closest_point
            else:
                self.temp_point.previous_name()
                final_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_line])
                self.temp_point.next()
                self.handle_point_creation(point=final_point)
            self.current_line.add_point(final_point)
            self.scene().shapes_manager.clear_temp_shapes(Line)
            self.scene().shapes_manager.add_shape(self.current_line)
            self.temp_point = None

    def handle_ray_creation(self, logical_pos, closest_point):
        if self.temp_point is None:  # Выбираем начальную точку луча.
            self.current_ray = Ray()  # Создаем пока пустой луч(без направления).
            if closest_point:  # Если рядом с курсором нашлась точка, то устанавливаем ее как начальную.
                closest_point.add_to_owner(owner=self.current_ray)
                self.temp_point = closest_point
            else:  # Если не нашлась, то устанавливаем начальную точку по координатам курсора.
                self.temp_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_ray])
                self.handle_point_creation(point=self.temp_point)
            self.current_ray.add_point(self.temp_point)
        else:
            # Завершаем рисовать луч и добавляем его в список постоянных фигур (второе нажатие).
            if closest_point:
                closest_point.add_to_owner(owner=self.current_ray)
                final_point = closest_point
            else:
                self.temp_point.previous_name()
                final_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_ray])
                self.temp_point.next()
                self.handle_point_creation(point=final_point)
            self.current_ray.add_point(final_point)
            self.scene().shapes_manager.clear_temp_shapes(Ray)
            self.scene().shapes_manager.add_shape(self.current_ray)
            self.temp_point = None

    def handle_distance_tool(self, closest_point=False):
        if closest_point:
            if len(self.scene().shapes_manager.selected_points) == 0:
                self.scene().shapes_manager.add_selected_point(closest_point)
            else:
                self.scene().shapes_manager.add_selected_point(closest_point)
                message = (self.scene().shapes_manager.selected_points[0].name +
                           self.scene().shapes_manager.selected_points[1].name + "=" +
                           str(self.scene().shapes_manager.distance(self.scene().shapes_manager.selected_points)))
                x = (self.scene().shapes_manager.selected_points[0].x +
                     self.scene().shapes_manager.selected_points[1].x) / 2
                y = (self.scene().shapes_manager.selected_points[0].y +
                     self.scene().shapes_manager.selected_points[1].y) / 2
                self.scene().shapes_manager.add_shape(Inf(x, y, message))
                self.scene().shapes_manager.clear_selected_points()

    def handle_circle_creation(self, logical_pos, closest_point):
        if self.temp_point is None:  # Устанавливаем центр круга.
            self.current_circle = Circle()  # Создаем пока пустой круг.
            if closest_point:  # Если нашли ближайшую точку, используем её как центр.
                closest_point.add_to_owner(owner=self.current_circle)
                self.temp_point = closest_point
            else:  # Если не нашлась, выбираем для центра координаты цурсора.
                self.temp_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_circle])
                self.handle_point_creation(point=self.temp_point)
            self.current_circle.add_point(self.temp_point)
        else:
            # Завершаем рисовать круг и добавляем его в список постоянных фигур (второе нажатие).
            if closest_point:
                closest_point.add_to_owner(owner=self.current_circle)
                final_point = closest_point
            else:
                self.temp_point.previous_name()
                final_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_circle])
                self.temp_point.next()
                self.handle_point_creation(point=final_point)
            self.current_circle.add_point(final_point)
            self.scene().shapes_manager.clear_temp_shapes(Circle)
            self.scene().shapes_manager.add_shape(self.current_circle)
            self.temp_point = None

    def handle_segment_creation(self, logical_pos, closest_point):
        # Обрабатывает создание отрезка

        if self.temp_point is None:  # Т.е. это наша первая точка
            self.current_segment = Segment()  # Создаем пока пустой отрезок
            if closest_point:  # Если нашли ближайшую точку, используем её как начало линии
                closest_point.add_to_owner(owner=self.current_segment)
                self.temp_point = closest_point
            else:  # Иначе устанавливаем текущую позицию
                self.temp_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_segment])
                self.handle_point_creation(point=self.temp_point)
            self.current_segment.add_point(self.temp_point)
        else:
            # Завершаем рисовать линию и добавляем её в список постоянных фигур (второе нажатие)
            if closest_point:
                closest_point.add_to_owner(owner=self.current_segment)
                final_point = closest_point
            else:
                self.temp_point.previous_name()
                final_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_segment])
                self.temp_point.next()
                self.handle_point_creation(point=final_point)
            self.current_segment.add_point(final_point)
            self.scene().shapes_manager.clear_temp_shapes(Segment)
            self.scene().shapes_manager.add_shape(self.current_segment)
            self.temp_point = None

    def handle_polygon_creation(self, logical_pos, closest_point):
        # Обрабатывает создание многоугольника

        if self.polygon_points is None:  # Т.е. это наша первая точка
            self.current_polygon = Polygon()
            self.polygon_points = []

        # Если ближайшая точка найдена и это начальная точка многоугольника, то завершаем рисование
        if closest_point and self.polygon_points and closest_point == self.polygon_points[0]:
            if len(self.polygon_points) > 1:  # Создаем линию от последней точки к первой
                last_point = self.polygon_points[-1]
                self.scene().shapes_manager.add_shape(
                    Segment([last_point, closest_point], owner=[self.current_polygon]))
            self.scene().shapes_manager.clear_temp_shapes(Segment)
            self.scene().shapes_manager.add_shape(self.current_polygon)
            self.polygon_points = None
        else:
            # Добавляем новую точку (не первую)
            if closest_point:
                closest_point.add_to_owner(self.current_polygon)
                new_point = closest_point
            else:
                new_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_polygon])
                self.handle_point_creation(point=new_point)
            if not self.polygon_points or (self.polygon_points and new_point != self.polygon_points[-1]):
                if self.polygon_points:
                    last_point = self.polygon_points[-1]
                    self.scene().shapes_manager.add_shape(
                        Segment([last_point, new_point], owner=[self.current_polygon]))
                self.polygon_points.append(new_point)
                if len(self.polygon_points) == 1:
                    new_point.previous_name()
                self.current_polygon.add_point(new_point)

        self.scene().shapes_manager.clear_temp_shapes(Segment)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        scene_pos = self.mapToScene(event.pos())
        logical_pos = self.scene().to_logical_coords(scene_pos.x(), scene_pos.y())
        if self.grid_gravity_mode:
            gravity_coordinates = (round(logical_pos[0] / self.scene().grid_step) * self.scene().grid_step,
                                   round(logical_pos[1] / self.scene().grid_step) * self.scene().grid_step)
            if self.scene().shapes_manager.distance([Point(gravity_coordinates[0], gravity_coordinates[1]),
                                                     Point(logical_pos[0],
                                                           logical_pos[1])]) < self.scene().grid_step / 4:
                logical_pos = gravity_coordinates
        closest_point = self.scene().shapes_manager.find_closest_point(logical_pos[0], logical_pos[1],
                                                                       10 / self.scene().zoom_factor)  # Ближайшие точки
        closest_line = self.scene().shapes_manager.find_closest_line(logical_pos[0], logical_pos[1],
                                                                     10 / self.scene().zoom_factor)  # Ближайшая линия
        if self.current_tool in ['Point', 'Segment', 'Polygon', 'Line', 'Ray', 'Circle']:
            self.drawing_tools[self.current_tool](logical_pos=logical_pos, closest_point=closest_point)
        else:
            if self.current_tool in ['Parallel_Line', 'Perpendicular_Line']:
                self.drawing_tools[self.current_tool](logical_pos=logical_pos, closest_point=closest_point,
                                                      closest_line=closest_line)
            elif self.current_tool == 'Distance':
                self.handle_distance_tool(closest_point=closest_point)
            elif self.current_tool == 'Move':
                self.handle_move_canvas(scene_pos=scene_pos)

        self.scene().update_scene()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        scene_pos = self.mapToScene(event.pos())  # Преобразует координаты курсора в координаты сцены
        logical_pos = self.scene().to_logical_coords(scene_pos.x(),
                                                     scene_pos.y())  # Преобразует координаты сцены в логические координаты

        # print(f"Logical coordinates: {logical_pos}")
        # print(f"scene_pos: {scene_pos.x(), scene_pos.y()}")

        if self.current_tool == 'Move' and self.startMove:
            delta = (scene_pos - self.startMovePoint)
            self.scene().base_point[0] = self.saveBasePointX + delta.x()
            self.scene().base_point[1] = self.saveBasePointY + delta.y()

        self.initiate_temp_shape_drawing(logical_pos)
        self.scene().update_scene()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.startMove = False

    def keyPressEvent(self, event):
        step = 10
        # Перемещение, зум, переключение инструментов
        if event.key() == Qt.Key_Equal:
            self.scene().set_zoom_factor(self.scene().zoom_factor * 1.1)
        if event.key() == Qt.Key_Minus:
            self.scene().set_zoom_factor(self.scene().zoom_factor / 1.1)
        if event.key() == Qt.Key_W:
            self.scene().base_point[1] += step
        elif event.key() == Qt.Key_S:
            self.scene().base_point[1] -= step
        elif event.key() == Qt.Key_A:
            self.scene().base_point[0] += step
        elif event.key() == Qt.Key_D:
            self.scene().base_point[0] -= step
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_E:
            self.current_tool = 'Line'
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_R:
            self.current_tool = 'Ray'
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_T:
            self.current_tool = 'Circle'
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_F:
            self.current_tool = 'Distance'
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_G:
            self.current_tool = 'Point'
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_H:
            self.current_tool = 'Segment'
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Y:
            self.current_tool = 'Polygon'
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_P:
            self.current_tool = 'Parallel_Line'
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_L:
            self.current_tool = 'Perpendicular_Line'

        self.scene().update_scene()
        super().keyPressEvent(event)
