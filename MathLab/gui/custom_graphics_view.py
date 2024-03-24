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
        self.polygon_points = None  # Список точек для текущего рисуемого многоугольника.
        self.temp_point = None  # Временная точка для начала сегмента.

        # Связывает название инструмента с методом, который будет вызван при нажатии на мышку при этом инструменте
        self.tools = {
            'Point': self.handle_point_creation,
            'Segment': self.handle_segment_creation,
            'Polygon': self.handle_polygon_creation,
            'Line': self.handle_line_creation,
            'Ray': self.handle_ray_creation
        }

        self.setRenderHint(QPainter.Antialiasing)  # Включение сглаживания
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        scene_pos = self.mapToScene(event.pos())  # Преобразует координаты курсора в координаты сцены
        logical_pos = self.scene().to_logical_coords(scene_pos.x(),
                                                     scene_pos.y())  # Преобразует координаты сцены в логические координаты

        print(f"Logical coordinates: {logical_pos}")
        print(f"scene_pos: {scene_pos.x(), scene_pos.y()}")

        self.initiate_temp_shape_drawing(logical_pos)
        self.scene().update_scene()

    def initiate_temp_shape_drawing(self, logical_pos):
        """
        Инициирует отрисовку временной фигуры в зависимости от инструмента, который выбран
        Для 'Segment' и 'Polygon' идет от последней точки до текущей позиции курсора (преоб. в логические
        координаты).
        """
        if  self.current_tool == 'Segment' and self.temp_point is not None:
            self.draw_temp_segment(
                self.temp_point,
                Point(logical_pos[0], logical_pos[1])
            )
        elif self.current_tool == 'Line'  and self.temp_point is not None:
            self.draw_temp_line(
                self.temp_point,
                Point(logical_pos[0], logical_pos[1])
            )
        elif self.current_tool == 'Ray'  and self.temp_point is not None:
            self.draw_temp_ray(
                self.temp_point,
                Point(logical_pos[0], logical_pos[1])
            )
        elif self.current_tool == 'Polygon' and self.polygon_points is not None and self.polygon_points:
            last_point = self.polygon_points[-1]
            self.draw_temp_segment(
                last_point,
                Point(logical_pos[0], logical_pos[1])
            )

    def draw_temp_ray(self, point_1, point_2, color=(37, 109, 133, 200)):
        # Добавляет временную линию в shapes_manager для дальнейшей отрисовки. Принимает точки класса Point
        self.scene().shapes_manager.clear_temp_rays()
        ray = Ray(points=[point_1, point_2], color=color)
        self.scene().shapes_manager.add_temp_ray(ray)
    def draw_temp_line(self, point_1, point_2, color=(37, 109, 133, 200)):
        # Добавляет временную линию в shapes_manager для дальнейшей отрисовки. Принимает точки класса Point
        self.scene().shapes_manager.clear_temp_lines()
        line = Line(points=[point_1, point_2], color=color)
        self.scene().shapes_manager.add_temp_line(line)

    def draw_temp_segment(self, point_1, point_2, color=(37, 109, 133, 200)):
        # Добавляет временную линию в shapes_manager для дальнейшей отрисовки. Принимает точки класса Point
        self.scene().shapes_manager.clear_temp_segments()
        segment = Segment(points=[point_1, point_2], color=color)
        self.scene().shapes_manager.add_temp_segment(segment)

    def handle_point_creation(self, logical_pos=None, point=None, closest_point=False):
        """
        Добавляет точку на сцену.
        Может принимать для этого как логические координаты (для инструмента Point),
        так и точку (сделано как костыль для других инструментов)
        """
        if not closest_point:  # Добавляет новую только тогда, когда не найдена точка в ближайшем радиусе
            if logical_pos is not None:
                point = Point(logical_pos[0], logical_pos[1])
            self.scene().shapes_manager.add_shape(point)

    def handle_line_creation(self,logical_pos, closest_point):
        if self.temp_point is None:  # Т.е. это наша первая точка
            self.current_line = Line()  # Создаем пока пустой отрезок
            if closest_point:  # Если нашли ближайшую точку, используем её как начало линии
                closest_point.add_to_owner(owner=self.current_line)
                self.temp_point = closest_point
            else:  # Иначе устанавливаем текущую позицию
                self.temp_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_line])
                self.handle_point_creation(point=self.temp_point)
            self.current_line.add_point(self.temp_point)
        else:
            # Завершаем рисовать линию и добавляем её в список постоянных фигур (второе нажатие)
            if closest_point:
                closest_point.add_to_owner(owner=self.current_line)
                final_point = closest_point
            else:
                final_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_line])
                self.handle_point_creation(point=final_point)
            self.current_line.add_point(final_point)
            self.scene().shapes_manager.clear_temp_lines()
            self.scene().shapes_manager.add_shape(self.current_line)
            self.temp_point = None

    def handle_ray_creation(self,logical_pos, closest_point):
        if self.temp_point is None:  # Т.е. это наша первая точка
            self.current_ray = Ray()  # Создаем пока пустой отрезок
            if closest_point:  # Если нашли ближайшую точку, используем её как начало линии
                closest_point.add_to_owner(owner=self.current_ray)
                self.temp_point = closest_point
            else:  # Иначе устанавливаем текущую позицию
                self.temp_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_ray])
                self.handle_point_creation(point=self.temp_point)
            self.current_ray.add_point(self.temp_point)
        else:
            # Завершаем рисовать линию и добавляем её в список постоянных фигур (второе нажатие)
            if closest_point:
                closest_point.add_to_owner(owner=self.current_ray)
                final_point = closest_point
            else:
                final_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_ray])
                self.handle_point_creation(point=final_point)
            self.current_ray.add_point(final_point)
            self.scene().shapes_manager.clear_temp_lines()
            self.scene().shapes_manager.add_shape(self.current_ray)
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
                final_point = Point(logical_pos[0], logical_pos[1], owner=[self.current_segment])
                self.handle_point_creation(point=final_point)
            self.current_segment.add_point(final_point)
            self.scene().shapes_manager.clear_temp_segments()
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
            self.scene().shapes_manager.clear_temp_segments()
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
                self.current_polygon.add_point(new_point)

        self.scene().shapes_manager.clear_temp_segments()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        scene_pos = self.mapToScene(event.pos())
        logical_pos = self.scene().to_logical_coords(scene_pos.x(), scene_pos.y())

        closest_point = self.scene().shapes_manager.find_closest_point(logical_pos[0], logical_pos[1],
                                                                       10 / self.scene().zoom_factor)  # Ближайшие точки
        self.tools[self.current_tool](logical_pos=logical_pos, closest_point=closest_point)
        """
        Я пока удалила "Удаление", т.к. это должен быть отдельный инструмент со своей логикой

            elif event.button() == Qt.RightButton:
                shape = self.scene().shapes_manager.find_shape(logical_pos[0], logical_pos[1], 10 / self.scene().zoom_factor)
                if shape:
                    self.scene().shapes_manager.remove_shape(shape)
        """
        """
        Для отладки, чтобы было на всякий случай
        for sh in self.scene().shapes_manager.shapes:
            for s in self.scene().shapes_manager.shapes[sh]:
                print(f"{sh}\t|\t{type(s)}\t|\t{s.owner}")
        print("------------------------")
        """
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
        elif event.key()==Qt.Key_E:
            if self.current_tool == 'Point':
                self.current_tool = 'Line'
            else:
                self.current_tool = 'Point'
        elif event.key()==Qt.Key_R:
            if self.current_tool == 'Point':
                self.current_tool = 'Ray'
            else:
                self.current_tool = 'Point'
        elif event.key() == Qt.Key_Q:
            if self.current_tool == 'Point':
                self.current_tool = 'Segment'
            elif self.current_tool == 'Segment':
                self.current_tool = 'Polygon'
            else:
                self.current_tool = 'Point'

        self.scene().update_scene()
        super().keyPressEvent(event)
