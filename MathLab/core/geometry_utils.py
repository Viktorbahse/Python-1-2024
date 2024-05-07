from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import *
import sympy as sp


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
