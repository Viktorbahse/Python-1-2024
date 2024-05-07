from PyQt5.QtWidgets import QGraphicsView, QShortcut
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence, QCursor, QPixmap
from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import *
from core.geometry_utils import *
from tests.timing import *
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
import sympy as sp
import time


class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.max_zoom_factor = 1e+16
        self.min_zoom_factor = 1e-11
        self.zoom_multiplier = 1.05

        self.startMove = False
        self.current_tool = 'Move'  # Текущий инструмент
        self.polygon_points = None  # Список точек для текущего рисуемого многоугольника.
        self.temp_point = None  # Временная точка для начала сегмента.
        self.temp_point1 = None
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
            'Parallel Line': self.handle_parallel_line_creation,
            'Perpendicular Line': self.handle_perpendicular_line_creation,
            'Midpoint': self.handle_midpoint_creation,
            'Perpendicular Bisector': self.handle_perpendicular_bisector_creation,
            'Angle Bisector': self.handle_angle_bisector_creation
        }

        self.setRenderHint(QPainter.Antialiasing)  # Включение сглаживания
        self.setMouseTracking(True)

    def initiate_temp_shape_drawing(self, logical_pos):
        # Инициирует отрисовку временной фигуры (добавляет временную фигуру в shapes_manager)
        temp_color = (37, 109, 133, 200)
        temp_shape = None

        if self.temp_line is not None and self.current_tool in ['Parallel Line', 'Perpendicular Line']:
            self.draw_temp_parallel_line(sp.Point(logical_pos[0], logical_pos[1]))
        elif self.temp_point is not None and self.temp_point.distance_to_shape(logical_pos[0], logical_pos[1]) != 0:
            if self.current_tool == 'Perpendicular Bisector':
                temp_shape = Line(color=temp_color)
                temp_shape.entity = (
                    sp.Line(self.temp_point.entity, sp.Point(logical_pos[0], logical_pos[1]))).perpendicular_line(
                    self.temp_point.entity.midpoint(sp.Point(logical_pos[0], logical_pos[1])))
            elif self.current_tool == 'Angle Bisector' and self.temp_point1 is not None:
                pass
                # temp_shape = Line()
                # temp_shape.entity = bisector(self.temp_point.entity, self.temp_point1.entity, sp.Point(logical_pos[0], logical_pos[1]))
            elif self.current_tool == 'Segment':
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
        line.entity = self.temp_line.parallel_line(point)
        line.set_color(color)  # Чтобы цвет временной линии был такой же, как у остальных
        self.scene().shapes_manager.add_temp_shape(line)

    def handle_move_canvas(self, scene_pos):
        self.startMove = True
        self.startMovePoint = scene_pos
        self.saveBasePointX = self.scene().base_point[0]
        self.saveBasePointY = self.scene().base_point[1]

    def handle_point_creation(self, logical_pos=None, point=None, closest_point=False, closest_shape=None):
        # Добавляет точку на сцену
        if not closest_point:  # Добавляет новую только тогда, когда не найдена точка в ближайшем радиусе
            if logical_pos is not None:
                point = Point(logical_pos[0], logical_pos[1])
            else:
                logical_pos = [None, None]
                logical_pos[0], logical_pos[1] = point.entity

            closest_shape = self.scene().shapes_manager.find_closest_shape(logical_pos[0], logical_pos[1],
                                                                           10 / self.scene().zoom_factor)
            lines = [shape for shape in closest_shape[2] if isinstance(shape, (Line, Segment, Ray, Circle))]
            # Находим лучшее местоположение для новой точки
            target_pos, target_lines = find_best_target(logical_pos, lines, radius=10 / self.scene().zoom_factor)
            point.entity = sp.Point(target_pos[0], target_pos[1])
            for line in target_lines:
                point.add_owner(line)
                line.add_secondary_element(point)
            self.scene().shapes_manager.add_shape(point)

    def handle_midpoint_creation(self, logical_pos=None, closest_point=False):
        if self.temp_point is None:  # Выбираем начальную точку линии.
            if closest_point:  # Если рядом с курсором нашлась точка, то устанавливаем ее как начальную.
                self.temp_point = closest_point
            else:  # Если не нашлась, то устанавливаем начальную точку по координатам курсора.
                self.temp_point = Point(logical_pos[0], logical_pos[1])
                self.handle_point_creation(point=self.temp_point)
        else:
            if closest_point:
                final_point = closest_point
            else:
                final_point = Point(logical_pos[0], logical_pos[1])
                self.handle_point_creation(point=final_point)

            if self.temp_point.distance_to_shape(final_point.entity.x, final_point.entity.y) != 0:
                coords = self.temp_point.entity.midpoint(final_point.entity)
                point = Point(coords.x, coords.y, owner=[self.temp_point, final_point])
                self.temp_point.add_secondary_element(point)
                final_point.add_secondary_element(point)

                self.handle_point_creation(point=point)
                self.temp_point = None

    def handle_perpendicular_bisector_creation(self, logical_pos, closest_point):
        if closest_point is not None:
            if self.temp_point is None:
                self.current_line = Line()
                self.current_line.add_owner(closest_point)
                closest_point.add_secondary_element(self.current_line)

                self.temp_point = closest_point
            else:
                self.current_line.add_owner(closest_point)
                closest_point.add_secondary_element(self.current_line)

                final_point = closest_point
                if self.temp_point.distance_to_shape(final_point.entity.x, final_point.entity.y) != 0:
                    self.scene().shapes_manager.clear_temp_shapes(Line)
                    self.current_line.entity = (sp.Line(self.temp_point.entity, final_point.entity)).perpendicular_line(
                        self.temp_point.entity.midpoint(final_point.entity))
                    self.scene().shapes_manager.add_shape(self.current_line)
                    self.temp_point = None

    def handle_angle_bisector_creation(self, logical_pos, closest_point):
        if closest_point is not None:

            if self.temp_point is None:
                self.current_line = Line()
                self.temp_point = closest_point
            self.current_line.add_owner(closest_point)
            closest_point.add_secondary_element(self.current_line)
            if self.temp_point1 is None and self.temp_point.distance_to_shape(closest_point.entity.x,
                                                                                closest_point.entity.y) != 0:
                self.temp_point1 = closest_point
            elif self.temp_point.distance_to_shape(closest_point.entity.x,
                                                   closest_point.entity.y) != 0 and self.temp_point1.distance_to_shape(
                closest_point.entity.x, closest_point.entity.y) != 0:
                final_point = closest_point

                self.scene().shapes_manager.clear_temp_shapes(Line)
                self.current_line.entity = bisector(self.temp_point.entity, self.temp_point1.entity, final_point.entity)
                self.scene().shapes_manager.add_shape(self.current_line)
                self.temp_point = None
                self.temp_point1 = None

    def handle_perpendicular_line_creation(self, logical_pos, closest_shape):
        if self.temp_line is None and self.temp_point is None:
            self.current_line = Line()  # Создаем пустую линию.
            if isinstance(closest_shape[0], (Segment, Line, Ray)):  # Если есть ближайшая линия
                self.current_line.add_owner(closest_shape[0])
                closest_shape[0].add_secondary_element(self.current_line)
                self.temp_line = closest_shape[0].entity.perpendicular_line(sp.Point(logical_pos[0], logical_pos[1]))
            else:
                if isinstance(closest_shape[0], Point):  # Если рядом с курсором нашлась точка, то устанавливаем ее как начальную.
                    closest_point = closest_shape[0]
                    self.temp_point = closest_point
                else:  # Если не нашлась, то устанавливаем начальную точку по координатам курсора.
                    self.temp_point = Point(logical_pos[0], logical_pos[1])
                    self.handle_point_creation(point=self.temp_point)
                self.current_line.add_owner(self.temp_point)
                self.temp_point.add_secondary_element(self.current_line)
                # self.current_line.add_point(self.temp_point)
        elif self.temp_line is not None and self.temp_point is None:
            if isinstance(closest_shape[0], Point):
                # closest_point = closest_shape[0].add_owner(owner=self.current_line)
                final_point = closest_shape[0]
            else:
                final_point = Point(logical_pos[0], logical_pos[1])
                self.handle_point_creation(point=final_point)
            self.current_line.add_owner(final_point)
            final_point.add_secondary_element(self.current_line)

            self.current_line.entity = self.temp_line.parallel_line(
                sp.Point(final_point.entity.x, final_point.entity.y))
            self.scene().shapes_manager.clear_temp_shapes()
            self.scene().shapes_manager.add_shape(self.current_line)
            self.temp_point = None
            self.temp_line = None
        elif self.temp_line is None and self.temp_point is not None:
            if isinstance(closest_shape[0], (Segment, Line, Ray)):
                self.temp_line = closest_shape[0]
                self.current_line.add_owner(self.temp_line)
                self.temp_line.add_secondary_element(self.current_line)

                self.current_line.entity = self.temp_line.entity.perpendicular_line(
                    sp.Point(self.temp_point.entity.x, self.temp_point.entity.y))
                self.scene().shapes_manager.clear_temp_shapes()
                self.scene().shapes_manager.add_shape(self.current_line)
                self.temp_point = None
                self.temp_line = None

    def handle_parallel_line_creation(self, logical_pos, closest_shape):
        if self.temp_line is None and self.temp_point is None:
            self.current_line = Line()  # Создаем пустую линию.
            if isinstance(closest_shape[0], (Segment, Line, Ray)):  # Если есть ближайшая линия
                self.current_line.add_owner(closest_shape[0])
                closest_shape[0].add_secondary_element(self.current_line)
                self.temp_line = closest_shape[0].entity
            else:
                if isinstance(closest_shape[0], Point):  # Если рядом с курсором нашлась точка, то устанавливаем ее как начальную.
                    closest_point = closest_shape[0]
                    self.temp_point = closest_point
                else:  # Если не нашлась, то устанавливаем начальную точку по координатам курсора.
                    self.temp_point = Point(logical_pos[0], logical_pos[1])
                    self.handle_point_creation(point=self.temp_point)
                self.current_line.add_owner(self.temp_point)
                self.temp_point.add_secondary_element(self.current_line)
                # self.current_line.add_point(self.temp_point)
        elif self.temp_line is not None and self.temp_point is None:
            if isinstance(closest_shape[0], Point):
                #closest_point = closest_shape[0].add_owner(owner=self.current_line)
                final_point = closest_shape[0]
            else:
                final_point = Point(logical_pos[0], logical_pos[1])
                self.handle_point_creation(point=final_point)
            self.current_line.add_owner(final_point)
            final_point.add_secondary_element(self.current_line)

            self.current_line.entity = self.temp_line.parallel_line(
                sp.Point(final_point.entity.x, final_point.entity.y))
            self.scene().shapes_manager.clear_temp_shapes()
            self.scene().shapes_manager.add_shape(self.current_line)
            self.temp_point = None
            self.temp_line = None
        elif self.temp_line is None and self.temp_point is not None:
            if isinstance(closest_shape[0], (Segment, Line, Ray)):
                self.temp_line = closest_shape[0]
                self.current_line.add_owner(self.temp_line)
                self.temp_line.add_secondary_element(self.current_line)

                self.current_line.entity = self.temp_line.entity.parallel_line(
                    sp.Point(self.temp_point.entity.x, self.temp_point.entity.y))
                self.scene().shapes_manager.clear_temp_shapes()
                self.scene().shapes_manager.add_shape(self.current_line)
                self.temp_point = None
                self.temp_line = None

    def handle_line_creation(self, logical_pos, closest_point):
        if self.temp_point is None:  # Выбираем начальную точку линии.
            self.current_line = Line()  # Создаем пустую линию.
            if closest_point:  # Если рядом с курсором нашлась точка, то устанавливаем ее как начальную.
                closest_point.add_owner(owner=self.current_line)
                self.temp_point = closest_point
            else:  # Если не нашлась, то устанавливаем начальную точку по координатам курсора.
                self.temp_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_line])
                self.handle_point_creation(point=self.temp_point)
            self.current_line.add_point(self.temp_point)
        else:
            # Завершаем рисовать линию и добавляем её в список постоянных фигур (второе нажатие)
            if closest_point:
                closest_point.add_owner(owner=self.current_line)
                final_point = closest_point
            else:
                final_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_line])
                self.handle_point_creation(point=final_point)

            if self.temp_point.distance_to_shape(final_point.entity.x, final_point.entity.y) != 0:
                self.current_line.add_point(final_point)
                self.scene().shapes_manager.clear_temp_shapes(Line)
                self.scene().shapes_manager.add_shape(self.current_line)
                self.temp_point = None

    def handle_ray_creation(self, logical_pos, closest_point):
        if self.temp_point is None:  # Выбираем начальную точку луча.
            self.current_ray = Ray()  # Создаем пока пустой луч(без направления).
            if closest_point:  # Если рядом с курсором нашлась точка, то устанавливаем ее как начальную.
                closest_point.add_owner(owner=self.current_ray)
                self.temp_point = closest_point
            else:  # Если не нашлась, то устанавливаем начальную точку по координатам курсора.
                self.temp_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_ray])
                self.handle_point_creation(point=self.temp_point)
            self.current_ray.add_point(self.temp_point)
        else:
            # Завершаем рисовать луч и добавляем его в список постоянных фигур (второе нажатие).
            if closest_point:
                closest_point.add_owner(owner=self.current_ray)
                final_point = closest_point
            else:
                final_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_ray])
                self.handle_point_creation(point=final_point)
            if self.temp_point.distance_to_shape(final_point.entity.x, final_point.entity.y) != 0:
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
                x = (self.scene().shapes_manager.selected_points[0].entity.x +
                     self.scene().shapes_manager.selected_points[1].entity.x) / 2
                y = (self.scene().shapes_manager.selected_points[0].entity.y +
                     self.scene().shapes_manager.selected_points[1].entity.y) / 2
                self.scene().shapes_manager.add_shape(Inf(x, y, message))
                self.scene().shapes_manager.clear_selected_points()

    def handle_circle_creation(self, logical_pos, closest_point):
        if self.temp_point is None:  # Устанавливаем центр круга.
            self.current_circle = Circle()  # Создаем пока пустой круг.
            if closest_point:  # Если нашли ближайшую точку, используем её как центр.
                closest_point.add_owner(owner=self.current_circle)
                self.temp_point = closest_point
            else:  # Если не нашлась, выбираем для центра координаты цурсора.
                self.temp_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_circle])
                self.handle_point_creation(point=self.temp_point)
            self.current_circle.add_point(self.temp_point)
        else:
            # Завершаем рисовать круг и добавляем его в список постоянных фигур (второе нажатие).
            if closest_point:
                closest_point.add_owner(owner=self.current_circle)
                final_point = closest_point
            else:
                final_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_circle])
                self.handle_point_creation(point=final_point)
            if self.temp_point.distance_to_shape(final_point.entity.x, final_point.entity.y) != 0:
                self.current_circle.add_point(final_point)
                self.scene().shapes_manager.clear_temp_shapes(Circle)
                self.scene().shapes_manager.add_shape(self.current_circle)
                self.temp_point = None

    def handle_segment_creation(self, logical_pos, closest_point):
        # Обрабатывает создание отрезка
        if self.temp_point is None:  # Т.е. это наша первая точка
            self.current_segment = Segment()  # Создаем пока пустой отрезок
            if closest_point:  # Если нашли ближайшую точку, используем её как начало линии
                closest_point.add_owner(owner=self.current_segment)
                self.temp_point = closest_point
            else:  # Иначе устанавливаем текущую позицию
                self.temp_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_segment])
                self.handle_point_creation(point=self.temp_point)
            self.current_segment.add_point(self.temp_point)
        else:
            # Завершаем рисовать линию и добавляем её в список постоянных фигур (второе нажатие)
            if closest_point:
                closest_point.add_owner(owner=self.current_segment)
                final_point = closest_point
            else:
                final_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_segment])
                self.handle_point_creation(point=final_point)
            if self.temp_point.distance_to_shape(final_point.entity.x, final_point.entity.y) != 0:
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
                new_segment = Segment([last_point, closest_point], owner=[self.current_polygon])
                self.scene().shapes_manager.add_shape(new_segment)

                last_point.add_owner(new_segment)
                closest_point.add_owner(new_segment)

                self.current_polygon.add_secondary_element(new_segment)
                self.current_polygon.add_primary_element(new_segment)

            self.scene().shapes_manager.clear_temp_shapes(Segment)
            self.scene().shapes_manager.add_shape(self.current_polygon)
            self.polygon_points = None
        else:
            # Добавляем новую точку (не первую)
            if closest_point:
                closest_point.add_owner(self.current_polygon)
                new_point = closest_point
            else:
                new_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_polygon])
                self.handle_point_creation(point=new_point)
            if not self.polygon_points or (self.polygon_points and new_point != self.polygon_points[-1]):
                if self.polygon_points:
                    last_point = self.polygon_points[-1]
                    new_segment = Segment([last_point, new_point], owner=[self.current_polygon])
                    self.scene().shapes_manager.add_shape(new_segment)

                    last_point.add_owner(new_segment)
                    new_point.add_owner(new_segment)

                    self.current_polygon.add_secondary_element(new_segment)
                    self.current_polygon.add_primary_element(new_segment)
                self.polygon_points.append(new_point)
                self.current_polygon.add_point(new_point)

        self.scene().shapes_manager.clear_temp_shapes(Segment)

    def handle_delete(self, shape):
        # Метод для корректного удаления объектов

        for element in shape.primary_elements:  # Сначала удаляем основные элементы (продолжают жить без shape)
            element.remove_owner(shape)

        if shape.owner:
            while len(shape.owner) != 0:
                owner = shape.owner[0]

                # Если наша точка не является основной, то она удаляется без всяких последствий для owner
                if shape in owner.secondary_elements:
                    owner.remove_secondary_element(shape)
                # Иначе - удаляется сам owner
                else:
                    owner.remove_primary_element(shape)
                    self.handle_delete(owner)
        while len(shape.secondary_elements) != 0:  # Удаляем все второстепенные элементы (не сущ без shape)
            element = shape.secondary_elements[0]
            shape.remove_secondary_element(element)
            self.handle_delete(element)  # Запускаем рекурсию

        self.scene().shapes_manager.remove_shape(shape)

    def change_cursor(self):
        # Метод для изменения курсора
        if self.current_tool == 'Eraser':
            pixmap = QPixmap(10, 10)
            pixmap.fill(Qt.transparent)  # Заполняем прозрачным цветом
            painter = QPainter(pixmap)
            painter.setPen(Qt.black)
            painter.drawRect(0, 0, 9, 9)  # Рисуем квадрат
            painter.end()

            # Создаём курсор из QPixmap
            cursor = QCursor(pixmap)
            self.setCursor(cursor)  # Устанавливаем курсор для QGraphicsView

    # @timeit
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        scene_pos = self.mapToScene(event.pos())
        logical_pos = self.scene().to_logical_coords(scene_pos.x(), scene_pos.y())
        closest_shape = self.scene().shapes_manager.find_closest_shape(logical_pos[0], logical_pos[1],
                                                                       10 / self.scene().zoom_factor)

        closest_point = next((shape for shape in closest_shape[2] if isinstance(shape, Point)), None)  # Ближайшая точка

        if self.grid_gravity_mode:
            gravity_coordinates = (round(logical_pos[0] / self.scene().grid_step) * self.scene().grid_step,
                                   round(logical_pos[1] / self.scene().grid_step) * self.scene().grid_step)
            if self.scene().shapes_manager.distance([Point(gravity_coordinates[0], gravity_coordinates[1]),
                                                     Point(logical_pos[0],
                                                           logical_pos[1])]) < self.scene().grid_step / 4:
                logical_pos = gravity_coordinates
        if self.current_tool in ['Point', 'Segment', 'Polygon', 'Line', 'Ray', 'Circle', 'Midpoint',
                                 'Perpendicular Bisector', 'Angle Bisector']:
            self.drawing_tools[self.current_tool](logical_pos=logical_pos, closest_point=closest_point)
        else:
            if self.current_tool in ['Parallel Line', 'Perpendicular Line']:
                self.drawing_tools[self.current_tool](logical_pos, closest_shape)
            elif self.current_tool == 'Distance':
                self.handle_distance_tool(closest_point=closest_point)
            elif self.current_tool == 'Move':
                self.handle_move_canvas(scene_pos=scene_pos)
            elif self.current_tool == 'Eraser':
                self.change_cursor()
                if closest_shape[0]:  # Если найдена ближайшая фигура
                    self.handle_delete(closest_shape[0])

        self.scene().update_scene()

        # TODO: (Winter) find_closest_shape есть в handle_point, нужно убрать

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
        elif self.current_tool == 'Eraser' and event.buttons() == Qt.LeftButton:
            self.change_cursor()
            closest_shape = self.scene().shapes_manager.find_closest_shape(logical_pos[0], logical_pos[1],
                                                                           10 / self.scene().zoom_factor)
            if closest_shape[0]:  # Если найдена ближайшая фигура
                self.handle_delete(closest_shape[0])

        self.initiate_temp_shape_drawing(logical_pos)
        self.scene().update_scene()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.unsetCursor()  # Ставит обычный курсор после разжатия мыши
        self.startMove = False

    def keyPressEvent(self, event):
        step = 10

        # Получаем координаты курсора (сценические)
        cursor_pos = self.mapToScene(self.mapFromGlobal(QCursor.pos()))
        # Проверяем, находится ли курсор на нашем холсте
        if not self.sceneRect().contains(cursor_pos):
            cursor_pos = None  # Если нет, то приближаться будем не к точке, а к центру

        # Перемещение, зум, переключение инструментов
        if event.key() == Qt.Key_Equal:
            if self.scene().zoom_factor * self.zoom_multiplier <= self.max_zoom_factor:
                self.scene().set_zoom_factor(self.scene().zoom_factor * self.zoom_multiplier, cursor_pos)
        if event.key() == Qt.Key_Minus:
            if self.scene().zoom_factor / self.zoom_multiplier >= self.min_zoom_factor:
                self.scene().set_zoom_factor(self.scene().zoom_factor / self.zoom_multiplier, cursor_pos)
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
            self.current_tool = 'Parallel Line'
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_L:
            self.current_tool = 'Perpendicular Line'
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_M:
            self.current_tool = 'Midpoint'
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_K:
            self.current_tool = 'Perpendicular Bisector'
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_J:
            self.current_tool = 'Angle Bisector'
        elif event.key() == Qt.Key_Delete:
            self.current_tool = 'Eraser'
        self.scene().update_scene()
        super().keyPressEvent(event)
