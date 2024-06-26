from core.geometric_objects.geom_obj import *
from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import *
import sympy as sp
import copy


class MoveShapeCommand:
    def __init__(self, custom_graphics_view, shape, old_position, new_position):
        self.custom_graphics_view = custom_graphics_view
        self.shape = shape  # Фигура, которая будет перемещена
        self.old_position = old_position
        self.new_position = new_position

    def execute(self):
        # Перемещение фигуры в новое положение
        if isinstance(self.shape, Point):
            self.custom_graphics_view.handle_point_movement(self.shape, self.new_position)
        else:
            delta = sp.Point(*self.new_position) - sp.Point(*self.old_position)
            self.custom_graphics_view.handle_line_movement(self.shape, delta=delta)

    def undo(self):
        # Отмена перемещения фигуры и возврат в предыдущее положение
        if isinstance(self.shape, Point):
            self.custom_graphics_view.handle_point_movement(self.shape, self.old_position)
        else:
            delta = sp.Point(*self.old_position) - sp.Point(*self.new_position)
            self.custom_graphics_view.handle_line_movement(self.shape, delta=delta)


class CreateShapeCommand:
    def __init__(self, custom_graphics_view, shapes):
        self.custom_graphics_view = custom_graphics_view
        self.shapes = sorted(shapes, key=sort_key)
        self.shapes_copy = {shape: shape.get_info() for shape in shapes}

    def execute(self):
        # Создание фигуры
        for shape, copied_shape in zip(self.shapes, self.shapes_copy):
            new_shape_info = self.shapes_copy[shape]
            for key, value in new_shape_info.items():
                setattr(shape, key, value)  # Копирование данных

        for shape in self.shapes:
            if isinstance(shape, Polygon):
                for element in shape.primary_elements:
                    if isinstance(element, Segment):
                        shape.add_secondary_element(element)
            for element in shape.primary_elements:
                element.add_owner(shape)
            for element in shape.secondary_elements:
                element.add_owner(shape)
            for owner in shape.proportions:
                owner.add_secondary_element(shape)
            self.custom_graphics_view.scene().shapes_manager.add_shape(shape)

    def undo(self):
        for shape in self.shapes:
            self.custom_graphics_view.handle_delete(shape)


class DeleteShapeCommand:
    def __init__(self, custom_graphics_view, shapes):
        self.custom_graphics_view = custom_graphics_view
        self.shapes = sorted(list(shapes.keys()), key=sort_key)
        self.shapes_info = shapes

    def execute(self):
        for shape in self.shapes:
            self.custom_graphics_view.handle_delete(shape)

    def undo(self):
        for shape in self.shapes:
            new_shape_info = self.shapes_info[shape]
            for key, value in new_shape_info.items():
                setattr(shape, key, value)

        for shape in self.shapes:
            if isinstance(shape, Polygon):
                for element in shape.primary_elements:
                    if isinstance(element, Segment):
                        shape.add_secondary_element(element)
            for element in shape.primary_elements:
                element.add_owner(shape)
            for element in shape.secondary_elements:
                element.add_owner(shape)
            for owner in shape.proportions:
                owner.add_secondary_element(shape)
            self.custom_graphics_view.scene().shapes_manager.shapes[type(shape)].append(shape)


def sort_key(shape):
    if isinstance(shape, Polygon):
        return 0
    elif isinstance(shape, Point):
        return 2
    else:
        return 1
