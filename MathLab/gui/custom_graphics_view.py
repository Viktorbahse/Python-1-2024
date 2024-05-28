from PyQt5.QtWidgets import QGraphicsView, QShortcut
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QKeySequence, QCursor, QPixmap
from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import *
from core.geometry_utils import *
from core.redo_undo import *
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

        self.command_stack = []  # Список команд
        self.current_index = -1
        self.shapes_before = []

        self.current_tool = 'Move'  # Текущий инструмент
        self.polygon_points = None  # Список точек для текущего рисуемого многоугольника.
        self.temp_point = None  # Временная точка для начала сегмента.
        self.temp_point1 = None
        self.temp_line = None

        self.start_move = False
        self.start_move_point = None  # Точка начала перемещения
        self.moving_shape = None  # Перемещаемый объект

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
        if not isinstance(self.temp_line, sp.Line2D):  # Что-то страшное происходило в перпендикулярах, там трогать не стала
            line.entity = self.temp_line.entity.parallel_line(point)
        else:
            line.entity = self.temp_line.parallel_line(point)
        line.set_color(color)  # Чтобы цвет временной линии был такой же, как у остальных
        self.scene().shapes_manager.add_temp_shape(line)

    def handle_point_creation(self, logical_pos=None, point=None, closest_point=False):
        # Добавляет точку на сцену
        if not closest_point:  # Добавляет новую только тогда, когда не найдена точка в ближайшем радиусе
            if logical_pos is not None:
                point = Point(logical_pos[0], logical_pos[1])
                self.execute_command(CreateShapeCommand(self, [point], is_deepcopy=True))
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
                if isinstance(line, Circle):
                    a = sp.Point([line.primary_elements[0].entity.x, line.primary_elements[0].entity.y])
                    b = sp.Point([line.primary_elements[1].entity.x, line.primary_elements[1].entity.y])
                    formula = lambda a=a, b=b, c=point, a_new=line.primary_elements[0], b_new=line.primary_elements[1], is_circle=True, use_nearest_intersection=False: \
                        (update_secondary_point_coords(c, a, a_new, b, b_new, is_circle=is_circle, use_nearest_intersection=use_nearest_intersection))
                    point.set_proportion(line.primary_elements[0], formula)
                    point.set_proportion(line.primary_elements[1], formula)
                    point.set_proportion(line, formula)
                elif len(line.primary_elements) == 0:  # Странные чуваки
                    owner_points = []
                    for element in line.owner:
                        if isinstance(element, Point):
                            owner_points.append(element)
                    if len(owner_points) == 1:  # Если параллельная и так далее
                        owner_point = owner_points[0]
                    elif len(owner_points) == 3:  # Для биссектрисы
                        owner_point = owner_points[1]
                    a = sp.Point([owner_point.entity.x, owner_point.entity.y])
                    formula = lambda a=a, b=None, c=point, a_new=owner_point, b_new=None, line=line, use_nearest_intersection=False: ( 
                        update_secondary_point_coords(c, a, a_new, b, b_new, line=line, use_nearest_intersection=use_nearest_intersection))
                    point.set_proportion(owner_point, formula)
                    point.set_proportion(line, formula)
                elif len(line.primary_elements) == 2:
                    a = sp.Point([line.primary_elements[0].entity.x, line.primary_elements[0].entity.y])
                    b = sp.Point([line.primary_elements[1].entity.x, line.primary_elements[1].entity.y])
                    formula = lambda a=a, b=b, c=point, a_new=line.primary_elements[0], b_new=line.primary_elements[1], use_nearest_intersection=False: (
                        update_secondary_point_coords(c, a, a_new, b, b_new, use_nearest_intersection=use_nearest_intersection))
                    point.set_proportion(line.primary_elements[0], formula)
                    point.set_proportion(line.primary_elements[1], formula)
                    point.set_proportion(line, formula)

                line.add_secondary_element(point)
                point.add_connected_shape(line)
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
                formula = lambda p1=self.temp_point, p2=final_point: sp.Point(p1.entity.midpoint(p2.entity))
                coords = formula()
                point = Point(coords.x, coords.y, owner=[self.temp_point, final_point])
                self.temp_point.add_secondary_element(point, formula=formula)
                final_point.add_secondary_element(point, formula=formula)

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
                    formula = lambda p1=self.temp_point, p2=final_point: (
                        sp.Line(p1.entity, p2.entity).perpendicular_line(p1.entity.midpoint(p2.entity)))

                    self.current_line.entity = formula()
                    self.current_line.set_proportion(self.temp_point, formula)
                    self.current_line.set_proportion(final_point, formula)
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
            elif (self.temp_point.distance_to_shape(closest_point.entity.x, closest_point.entity.y) != 0 and
                  self.temp_point1.distance_to_shape(closest_point.entity.x, closest_point.entity.y) != 0):
                final_point = closest_point
                self.scene().shapes_manager.clear_temp_shapes(Line)

                formula = lambda p1=self.temp_point, p2=self.temp_point1, p3=final_point: (
                    bisector(p1.entity, p2.entity, p3.entity))
                self.current_line.entity = formula()
                self.current_line.set_proportion(self.temp_point, formula)
                self.current_line.set_proportion(self.temp_point1, formula)
                self.current_line.set_proportion(final_point, formula)

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
                self.primordial_shape = closest_shape[0]  # Для формулы мне нужна изначальная форма. По сути костыль
            else:
                if isinstance(closest_shape[0], Point):  # Если рядом с курсором нашлась точка, то устанавливаем ее как начальную.
                    closest_point = closest_shape[0]
                    self.temp_point = closest_point
                else:  # Если не нашлась, то устанавливаем начальную точку по координатам курсора.
                    self.temp_point = Point(logical_pos[0], logical_pos[1])
                    self.handle_point_creation(point=self.temp_point)
                self.current_line.add_owner(self.temp_point)
                self.temp_point.add_secondary_element(self.current_line)
        elif self.temp_line is not None and self.temp_point is None:
            if isinstance(closest_shape[0], Point):
                final_point = closest_shape[0]
            else:
                final_point = Point(logical_pos[0], logical_pos[1])
                self.handle_point_creation(point=final_point)
            self.current_line.add_owner(final_point)
            final_point.add_secondary_element(self.current_line)

            formula = lambda line=self.primordial_shape, p1=final_point: (
                line.entity.perpendicular_line(sp.Point(p1.entity.x, p1.entity.y)))
            self.current_line.entity = formula()
            self.current_line.set_proportion(self.primordial_shape, formula)
            self.current_line.set_proportion(final_point, formula)

            #self.current_line.entity = self.temp_line.parallel_line(
            #    sp.Point(final_point.entity.x, final_point.entity.y))
            self.scene().shapes_manager.clear_temp_shapes()
            self.scene().shapes_manager.add_shape(self.current_line)
            self.temp_point = None
            self.temp_line = None
        elif self.temp_line is None and self.temp_point is not None:
            if isinstance(closest_shape[0], (Segment, Line, Ray)):
                self.temp_line = closest_shape[0]
                self.current_line.add_owner(self.temp_line)
                self.temp_line.add_secondary_element(self.current_line)

                formula = lambda line=self.temp_line, p1=self.temp_point: (
                    line.entity.perpendicular_line(sp.Point(p1.entity.x, p1.entity.y)))
                self.current_line.entity = formula()
                self.current_line.set_proportion(self.temp_line, formula)
                self.current_line.set_proportion(self.temp_point, formula)

                #self.current_line.entity = self.temp_line.entity.perpendicular_line(
                    #sp.Point(self.temp_point.entity.x, self.temp_point.entity.y))
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
                self.temp_line = closest_shape[0]
            else:
                if isinstance(closest_shape[0], Point):  # Если рядом с курсором нашлась точка, то устанавливаем ее как начальную.
                    closest_point = closest_shape[0]
                    self.temp_point = closest_point
                else:  # Если не нашлась, то устанавливаем начальную точку по координатам курсора.
                    self.temp_point = Point(logical_pos[0], logical_pos[1])
                    self.handle_point_creation(point=self.temp_point)
                self.current_line.add_owner(self.temp_point)
                self.temp_point.add_secondary_element(self.current_line)
        elif self.temp_line is not None and self.temp_point is None:
            if isinstance(closest_shape[0], Point):
                final_point = closest_shape[0]
            else:
                final_point = Point(logical_pos[0], logical_pos[1])
                self.handle_point_creation(point=final_point)
            self.current_line.add_owner(final_point)
            final_point.add_secondary_element(self.current_line)

            formula = lambda line=self.temp_line, p1=final_point: (
                line.entity.parallel_line(sp.Point(p1.entity.x, p1.entity.y)))
            self.current_line.entity = formula()
            self.current_line.set_proportion(self.temp_line, formula)
            self.current_line.set_proportion(final_point, formula)

            #self.current_line.entity = self.temp_line.parallel_line(
            #    sp.Point(final_point.entity.x, final_point.entity.y))
            self.scene().shapes_manager.clear_temp_shapes()
            self.scene().shapes_manager.add_shape(self.current_line)
            self.temp_point = None
            self.temp_line = None
        elif self.temp_line is None and self.temp_point is not None:
            if isinstance(closest_shape[0], (Segment, Line, Ray)):
                self.temp_line = closest_shape[0]
                self.current_line.add_owner(self.temp_line)
                self.temp_line.add_secondary_element(self.current_line)

                formula = lambda line=self.temp_line, p1=self.temp_point: (
                    line.entity.parallel_line(sp.Point(p1.entity.x, p1.entity.y)))
                self.current_line.entity = formula()
                self.current_line.set_proportion(self.temp_line, formula)
                self.current_line.set_proportion(self.temp_point, formula)

                #self.current_line.entity = self.temp_line.entity.parallel_line(
                #    sp.Point(self.temp_point.entity.x, self.temp_point.entity.y))
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
                self.scene().shapes_manager.add_shape(Info(x, y, message))
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

    def handle_delete(self, shape, is_invisible=None):
        # Метод для корректного удаления объектов. Также достает и убирает объекты в невидимость
        if shape.primary_elements is None:  # Для undo\redo
            return
        for element in shape.primary_elements:  # Сначала удаляем основные элементы (продолжают жить без shape)
            element.remove_owner(shape, is_invisible=is_invisible)

        if shape.owner:
            len_owners = len(shape.owner)
            while len(shape.owner) != 0:
                if is_invisible and len_owners == 0:
                    break
                owner = shape.owner[len_owners - 1]

                # Если наша точка не является основной, то она удаляется без всяких последствий для owner
                if shape in owner.secondary_elements:
                    owner.remove_secondary_element(shape, is_invisible=is_invisible)
                # Иначе - удаляется сам owner
                else:
                    owner.remove_primary_element(shape, is_invisible=is_invisible)
                    if is_invisible:
                        if is_invisible == 1 and not owner.invisible:
                            owner.invisible = True
                            self.handle_delete(owner, is_invisible=is_invisible)
                        elif is_invisible == -1 and owner.invisible:
                            owner.invisible = False
                            self.handle_delete(owner, is_invisible=is_invisible)
                    else:
                        self.handle_delete(owner, is_invisible=is_invisible)
                len_owners -= 1
        len_sec_elem = len(shape.secondary_elements)
        while len(shape.secondary_elements) != 0:  # Удаляем все второстепенные элементы (не сущ без shape)
            if is_invisible and len_sec_elem == 0:
                break
            element = shape.secondary_elements[len_sec_elem - 1]
            shape.remove_secondary_element(element, is_invisible=is_invisible)
            len_sec_elem -= 1
            self.handle_delete(element, is_invisible=is_invisible)  # Запускаем рекурсию
        if not is_invisible:
            self.scene().shapes_manager.remove_shape(shape)
        else:
            if is_invisible == 1:
                shape.invisible = True
            elif is_invisible == -1:
                shape.invisible = False

    def handle_move_canvas(self, closest_shape=None):
        self.start_move = True
        if closest_shape and not isinstance(closest_shape, Polygon):
            self.moving_shape = closest_shape
        else:
            self.saveBasePointX = self.scene().base_point[0]
            self.saveBasePointY = self.scene().base_point[1]
        self.change_cursor()

    def handle_point_movement(self, point, logical_pos):
        in_owners_in_secondary = [element for element in point.owner if point in element.secondary_elements]  # Наверное можно использовать connected_shapes, но к моменту проверки всего кода я уже заябалась

        if logical_pos is None:  # Если точка уже переместилась (идет из handle_element_movement)
            pass  # Стоит намеренно, чтобы не заглядывать в другие случаи
        # Если точка в secondary_elements больше чем у 1 объекта, то она никуда не двигается
        elif len(in_owners_in_secondary) > 1:
            return
        elif len(in_owners_in_secondary) == 1:  # Может перемещаться только по объекту (его линии)
            new_point = sp.Point(logical_pos)
            if isinstance(in_owners_in_secondary[0], Circle):
                circle = in_owners_in_secondary[0].entity
                center = circle.center
                radius = circle.radius

                direction_vector = new_point - center
                direction_vector_length = sp.sqrt(direction_vector.x ** 2 + direction_vector.y ** 2)

                direction_unit_vector = direction_vector / direction_vector_length

                # Расчет проекции
                projected_point = center + radius * direction_unit_vector
                point.entity = projected_point.evalf()
            else:
                line = in_owners_in_secondary[0].entity
                perpendicular_line = line.perpendicular_line(new_point)
                intersection = line.intersection(perpendicular_line)
                if intersection:
                    projected_point = intersection[0]
                    point.entity = projected_point.evalf()
                else:
                    point.entity = line.points[0] \
                        if new_point.distance(line.points[0]) < new_point.distance(line.points[1]) else line.points[1]
        else:  # Обычный случай, когда перетаскивает пользователь
            new_position = self.grid_gravity(logical_pos)  # Применяем притяжение к сетке
            point.entity = sp.Point(new_position[0], new_position[1])

        for element in point.owner:
            if point in element.primary_elements:  # Если она primary_elem для объекта
                if isinstance(element, Polygon):
                    continue
                element.update_entity()
                self.handle_element_movement(element)

        for element in point.secondary_elements:
            if isinstance(element, Polygon):
                return
            element.entity = element.proportions[point]()
            self.handle_element_movement(element)

    def handle_line_movement(self, line, logical_pos=None, delta=None):  # Под линией имеются ввиду еще и окружности
        if delta is None:
            delta = sp.Point(*logical_pos) - sp.Point(*self.line_start_move_point)
        if any(point.connected_shapes for point in line.primary_elements):
            return
        for point in line.primary_elements:
            point.entity += delta
            self.handle_point_movement(point, logical_pos=None)
        if logical_pos is not None:
            self.line_start_move_point = logical_pos

    def handle_element_movement(self, element):
        for second_elem in element.secondary_elements:
            if isinstance(second_elem, Point):
                if len(second_elem.connected_shapes) <= 1:  # Если она не точка пересечения объектов
                    second_elem.entity = second_elem.proportions[element]()
                else:
                    new_coords = second_elem.proportions[element](use_nearest_intersection=True)
                    if new_coords is None:  # Если точки пересечения нет, то все в невидимость (если этого не было)
                        if not second_elem.invisible:
                            self.handle_delete(second_elem, is_invisible=1)
                        else:
                            continue
                    else:
                        second_elem.entity = new_coords
                        if second_elem.invisible:  # Если нашлись, то достаем из невидимости
                            self.handle_delete(second_elem, is_invisible=-1)
                        self.handle_point_movement(second_elem, None)
                        continue
                if isinstance(element, Circle):
                    a = sp.Point([element.primary_elements[0].entity.x, element.primary_elements[0].entity.y])
                    b = sp.Point([element.primary_elements[1].entity.x, element.primary_elements[1].entity.y])
                    formula = lambda a=a, b=b, c=second_elem, a_new=element.primary_elements[0], b_new=element.primary_elements[1], is_circle=True, use_nearest_intersection=False: (
                        update_secondary_point_coords(c, a, a_new, b, b_new, is_circle=is_circle, use_nearest_intersection=use_nearest_intersection))
                    second_elem.set_proportion(element.primary_elements[0], formula)
                    second_elem.set_proportion(element.primary_elements[1], formula)
                    second_elem.set_proportion(element, formula)
                elif len(element.primary_elements) == 2:
                    a = sp.Point([element.primary_elements[0].entity.x, element.primary_elements[0].entity.y])
                    b = sp.Point([element.primary_elements[1].entity.x, element.primary_elements[1].entity.y])
                    formula = lambda a=a, b=b, c=second_elem, a_new=element.primary_elements[0], b_new=element.primary_elements[1], use_nearest_intersection=False: (
                        update_secondary_point_coords(c, a, a_new, b, b_new, use_nearest_intersection=use_nearest_intersection))
                    second_elem.set_proportion(element.primary_elements[0], formula)
                    second_elem.set_proportion(element.primary_elements[1], formula)
                    second_elem.set_proportion(element, formula)
                elif len(element.primary_elements) == 0:
                    # elem - по идее такое должно быть только для параллельных и т.д.
                    # Надеемся, что у нас и дальше будет именно так, иначе - расписываем доп случаи
                    owner_points = []
                    for elem in element.owner:
                        if isinstance(elem, Point):
                            owner_points.append(elem)
                    if len(owner_points) == 1:  # Если параллельная и так далее
                        owner_point = owner_points[0]
                    elif len(owner_points) == 3:  # Для биссектрисы
                        owner_point = owner_points[1]

                    a = sp.Point([owner_point.entity.x, owner_point.entity.y])
                    formula = lambda a=a, b=None, c=second_elem, a_new=owner_point, b_new=None, line=element, use_nearest_intersection=False: (
                        update_secondary_point_coords(c, a, a_new, b, b_new, line, use_nearest_intersection=use_nearest_intersection))
                    second_elem.set_proportion(owner_point, formula)
                    second_elem.set_proportion(element, formula)
                self.handle_point_movement(second_elem, None)

            else:
                second_elem.entity = second_elem.proportions[element]()
                self.handle_element_movement(second_elem)

    def grid_gravity(self, logical_pos):
        # Притягивание к сетке
        if self.grid_gravity_mode:
            gravity_coordinates = (round(logical_pos[0] / self.scene().grid_step) * self.scene().grid_step,
                                   round(logical_pos[1] / self.scene().grid_step) * self.scene().grid_step)
            if self.scene().shapes_manager.distance([Point(gravity_coordinates[0], gravity_coordinates[1]),
                                                     Point(logical_pos[0],
                                                           logical_pos[1])]) < self.scene().grid_step / 4:
                return gravity_coordinates
        return logical_pos

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
        if self.current_tool == 'Move' and self.start_move:
            self.setCursor(Qt.PointingHandCursor)

    def execute_command(self, command, execute=False):
        # Добавление новой команды
        # Удаляем все команды, следующие за текущим индексом
        del self.command_stack[self.current_index + 1:]
        if execute:
            command.execute()

        self.command_stack.append(command)
        self.current_index += 1
        if len(self.command_stack) > 10:
            del self.command_stack[0]
            self.current_index -= 1

    def undo_last_command(self):
        # Отменяет последнюю команду
        if self.current_index >= 0:
            last_command = self.command_stack[self.current_index]
            last_command.undo()
            self.current_index -= 1
            self.scene().update_scene()

    def redo_last_command(self):
        # Возвращаем команду
        if self.current_index < len(self.command_stack) - 1:
            self.current_index += 1
            next_command = self.command_stack[self.current_index]
            next_command.execute()
            self.scene().update_scene()

    # @timeit
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        scene_pos = self.mapToScene(event.pos())
        logical_pos = self.scene().to_logical_coords(scene_pos.x(), scene_pos.y())
        closest_shape = self.scene().shapes_manager.find_closest_shape(logical_pos[0], logical_pos[1],
                                                                       10 / self.scene().zoom_factor)

        closest_point = next((shape for shape in closest_shape[2] if isinstance(shape, Point)), None)  # Ближайшая точка

        logical_pos = self.grid_gravity(logical_pos)
        if self.current_tool in ['Point', 'Segment', 'Polygon', 'Line', 'Ray', 'Circle', 'Midpoint',
                                 'Perpendicular Bisector', 'Angle Bisector']:
            temp_point_before = self.temp_point
            temp_point1_before = self.temp_point1
            temp_line_before = self.temp_line
            polygon_points_before = self.polygon_points

            self.drawing_tools[self.current_tool](logical_pos=logical_pos, closest_point=closest_point)

            if ((self.temp_point is None and temp_point_before != self.temp_point) or
                    (self.temp_point1 is None and temp_point1_before != self.temp_point1) or
                    (self.temp_line is None and temp_line_before != self.temp_line) or
                    (self.polygon_points is None and polygon_points_before != self.polygon_points)):
                shapes_after = [shape for shapes_list in self.scene().shapes_manager.shapes.values() for shape in shapes_list]
                added_shapes = [shape for shape in shapes_after if shape not in self.shapes_before]
                self.execute_command(CreateShapeCommand(self, added_shapes))
            if self.temp_point is None and self.temp_point1 is None and self.temp_line is None and self.polygon_points is None:
                self.shapes_before = [shape for shapes_list in self.scene().shapes_manager.shapes.values() for shape in shapes_list]
        else:
            if self.current_tool in ['Parallel Line', 'Perpendicular Line']:
                temp_point_before = self.temp_point
                temp_point1_before = self.temp_point1
                temp_line_before = self.temp_line
                polygon_points_before = self.polygon_points

                self.drawing_tools[self.current_tool](logical_pos, closest_shape)

                if ((self.temp_point is None and temp_point_before != self.temp_point) or
                        (self.temp_point1 is None and temp_point1_before != self.temp_point1) or
                        (self.temp_line is None and temp_line_before != self.temp_line) or
                        (self.polygon_points is None and polygon_points_before != self.polygon_points)):
                    shapes_after = [shape for shapes_list in self.scene().shapes_manager.shapes.values() for shape in
                                    shapes_list]
                    added_shapes = [shape for shape in shapes_after if shape not in self.shapes_before]
                    self.execute_command(CreateShapeCommand(self, added_shapes))
                if self.temp_point is None and self.temp_point1 is None and self.temp_line is None and self.polygon_points is None:
                    self.shapes_before = [shape for shapes_list in self.scene().shapes_manager.shapes.values() for shape
                                          in shapes_list]
            elif self.current_tool == 'Distance':
                self.handle_distance_tool(closest_point=closest_point)
            elif self.current_tool == 'Move':
                self.start_move_point = scene_pos
                self.line_start_move_point = logical_pos
                if closest_point:
                    self.handle_move_canvas(closest_shape=closest_point)
                else:
                    self.handle_move_canvas(closest_shape=closest_shape[0])
            elif self.current_tool == 'Eraser':
                self.change_cursor()
                closest_polygon = next((shape for shape in closest_shape[2] if isinstance(shape, Polygon)), None)
                self.shapes_before = [shape for shapes_list in self.scene().shapes_manager.shapes.values() for shape in
                                      shapes_list]

                if closest_polygon:
                    self.handle_delete(closest_polygon)
                elif closest_point:
                    self.handle_delete(closest_point)
                elif closest_shape[0]:
                    self.handle_delete(closest_shape[0])

        self.scene().update_scene()

        # TODO: (Winter) find_closest_shape есть в handle_point, нужно убрать
        # TODO: (Winter) После того, как применили Inf, closest_shape выдает его и все ломается

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        scene_pos = self.mapToScene(event.pos())  # Преобразует координаты курсора в координаты сцены
        logical_pos = self.scene().to_logical_coords(scene_pos.x(),
                                                     scene_pos.y())  # Преобразует координаты сцены в логические координаты

        if self.current_tool == 'Move' and self.start_move:
            if self.moving_shape:
                if isinstance(self.moving_shape, Point):
                    self.handle_point_movement(self.moving_shape, logical_pos)
                else:
                    self.handle_line_movement(self.moving_shape, logical_pos)
            else:
                delta = (scene_pos - self.start_move_point)
                self.scene().base_point[0] = self.saveBasePointX + delta.x()
                self.scene().base_point[1] = self.saveBasePointY + delta.y()
        elif self.current_tool == 'Eraser' and event.buttons() == Qt.LeftButton:
            self.change_cursor()
            closest_shape = self.scene().shapes_manager.find_closest_shape(logical_pos[0], logical_pos[1],
                                                                           10 / self.scene().zoom_factor)
            closest_polygon = next((shape for shape in closest_shape[2] if isinstance(shape, Polygon)), None)
            closest_point = next((shape for shape in closest_shape[2] if isinstance(shape, Point)), None)
            if closest_polygon:
                self.handle_delete(closest_polygon)
            elif closest_point:
                self.handle_delete(closest_point)
            elif closest_shape[0]:
                self.handle_delete(closest_shape[0])

        self.initiate_temp_shape_drawing(logical_pos)
        self.scene().update_scene()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.unsetCursor()  # Ставит обычный курсор после разжатия мыши
            if self.current_tool == "Eraser":
                shapes_after = [shape for shapes_list in self.scene().shapes_manager.shapes.values() for shape in
                                shapes_list]
                added_shapes = [shape for shape in shapes_after if shape not in self.shapes_before]
                self.execute_command(DeleteShapeCommand(self, added_shapes))

        if self.moving_shape is not None:
            scene_pos = self.mapToScene(event.pos())
            new_pos = self.scene().to_logical_coords(scene_pos.x(), scene_pos.y())
            old_pos = self.scene().to_logical_coords(self.start_move_point.x(), self.start_move_point.y())
            self.execute_command(MoveShapeCommand(self, self.moving_shape, old_pos, new_pos))
            self.moving_shape = None
        self.start_move = False

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
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_X:
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
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Z:
            self.undo_last_command()
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Y:
            self.redo_last_command()
        self.scene().update_scene()
        super().keyPressEvent(event)
