from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import *
import sympy as sp
import math


def bisector(a, b, c):
    ba = a - b
    bc = c - b
    ba_unit = ba / sp.sqrt(ba.dot(ba))
    bc_unit = bc / sp.sqrt(bc.dot(bc))
    bisector_unit = (ba_unit + bc_unit) / 2
    bisector_point = b + 1 * bisector_unit
    return sp.Line(sp.Point(float(b.x), float(b.y)), sp.Point(float(bisector_point.x), float(bisector_point.y)))


def find_best_target(logical_pos, lines, radius):
    # Ищет лучшую позицию для точки
    mouse_point = sp.Point2D(logical_pos[0], logical_pos[1])
    # Сортируем линии по расстоянию до точки
    sorted_lines = sorted(lines, key=lambda line: line.distance_to_shape(logical_pos[0], logical_pos[1]))

    if not sorted_lines:
        return logical_pos, []

    projection = sorted_lines[0].projection_onto_shape(mouse_point)
    best_target_pos = projection
    best_target_lines = [sorted_lines[0]]
    intersection_found = False  # Есть ли точка пересечения

    if len(sorted_lines) == 1:
        return best_target_pos, best_target_lines

    # Перебираем отсортированные линии, начинаем со второй
    for line in sorted_lines[1:]:
        if intersection_found:  # Если было точка пересечения, то остальные линии должны проходить через нее
            if line.contains(best_target_pos):
                best_target_lines.append(line)
        else:
            # Точка пересечения текущей линии с предыдущей
            intersection_points = line.entity.intersection(best_target_lines[0].entity)

            # Оставляем только те точки, которые лежат в нужном радиусе, и выбираем первую
            valid_intersection_points = [point for point in intersection_points if
                                         point and mouse_point.distance(point) <= radius]
            if valid_intersection_points:
                intersection_found = True
                best_target_pos = valid_intersection_points[0]
                best_target_lines.append(line)

    return best_target_pos, best_target_lines


def update_secondary_point_coords(c, a, a_new, b=None, b_new=None, line=None, is_circle=False, use_nearest_intersection=False):
    # Обновляет позицию точки c (формула для точки)

    if use_nearest_intersection:  # Если точка является точкой пересечения
        intersection_points = find_intersections(c.connected_shapes)
        closest_intersection_point = None
        min_distance = float('inf')
        for intersection_point in intersection_points:
            dist = c.entity.distance(intersection_point)
            if dist < min_distance:
                min_distance = dist
                closest_intersection_point = intersection_point

        if closest_intersection_point is None:
            return None
        return closest_intersection_point

    c = c.entity
    a_new = a_new.entity
    if b_new is not None:
        b_new = b_new.entity

    if b is None:  # Т.е. это параллельная линия, например
        delta_x = a_new.x - a.x
        delta_y = a_new.y - a.y
        c_new = sp.Point(c.x + delta_x, c.y + delta_y)
        if line.contains(c_new):
            return c_new

        # Если у нас меняется направление линии, а не точка а
        ac_distance = a.distance(c)
        direction_vector = line.entity.direction
        direction_vector = sp.Matrix([direction_vector.x, direction_vector.y])
        norm = sp.sqrt(direction_vector.dot(direction_vector))
        direction_unit_vector = direction_vector / norm

        vector_ac = c - a
        vector_ac_new = sp.Matrix([vector_ac.x, vector_ac.y])
        if vector_ac_new.dot(direction_vector) < 0:
            direction_unit_vector = -direction_unit_vector

        c_new = a_new + ac_distance * direction_unit_vector
        return c_new

    if a_new == a and b_new == b:  # Если ничего не изменилось
        return c

    if is_circle:
        # Работа с кругом, a — центр, b — точка на окружности
        if a_new != a:
            center = a_new
            radius = center.distance(b)
        elif b_new != b:
            center = a
            radius = center.distance(sp.Point(b_new))

        direction_vector = c - a
        direction_vector_len = sp.sqrt(direction_vector.x ** 2 + direction_vector.y ** 2)
        direction_unit_vector = direction_vector / direction_vector_len
        c_new = center + radius * direction_unit_vector
        return c_new

    if a_new != a:  # Случай с пропорциями
        moving_point = a
        fixed_point = b
        new_position = a_new
    elif b_new != b:
        moving_point = b
        fixed_point = a
        new_position = b_new

    if moving_point.x == new_position.x:  # x не меняется
        new_position_modified = sp.Point(new_position.x, new_position.y + 1)
    elif moving_point.y == new_position.y:  # y не меняется
        new_position_modified = sp.Point(new_position.x + 1, new_position.y)
    else:
        new_position_modified = new_position
    if fixed_point == new_position or moving_point == new_position_modified:
        return c

    moving_line_modified = sp.Line(moving_point, new_position_modified)
    static_moving_line = sp.Line(fixed_point, new_position)

    line_c_new = moving_line_modified.parallel_line(c)
    intersection_point = static_moving_line.intersection(line_c_new)
    if intersection_point:
        if isinstance(intersection_point[0], sp.Line2D):
            return c
        return intersection_point[0]


def find_intersections(shapes):  # Находит все пересечения объектов
    intersection_points = []

    for i in range(len(shapes)):
        for j in range(i + 1, len(shapes)):
            intersections = shapes[i].entity.intersect(shapes[j].entity)
            intersection_points.extend(intersections)
    return intersection_points
