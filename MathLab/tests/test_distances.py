import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import random
from core.geometric_objects.geom_obj import Point
from core.shapes_manager import ShapesManager


def generate_int_tests():
    cases = []
    for i in range(100):
        x_1, y_1, x_2, y_2 = [random.randint(-10 ** 16, 10 ** 16) for _ in range(4)]
        expected = ((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2) ** 0.5
        cases.append((x_1, y_1, x_2, y_2, expected))
    return cases


def generate_float_tests():
    cases = []
    for i in range(100):
        x_1, y_1, x_2, y_2 = [random.uniform(-10.0 ** 16, 10.0 ** 16) for _ in range(4)]
        expected = ((x_2 - x_1) ** 2 + (y_2 - y_1) ** 2) ** 0.5
        cases.append((x_1, y_1, x_2, y_2, expected))
    return cases


@pytest.mark.parametrize("x_1, y_1, x_2, y_2, expected", generate_int_tests())
def test_distance_int(x_1, y_1, x_2, y_2, expected):
    point_1 = Point(x_1, y_1)
    point_2 = Point(x_2, y_2)
    received_distance = ShapesManager.distance([point_1, point_2])
    assert round(received_distance, 8) == round(expected, 8)


@pytest.mark.parametrize("x_1, y_1, x_2, y_2, expected", generate_float_tests())
def test_distance_float(x_1, y_1, x_2, y_2, expected):
    point_1 = Point(x_1, y_1)
    point_2 = Point(x_2, y_2)
    received_distance = ShapesManager.distance([point_1, point_2])
    assert round(received_distance, 8) == round(expected, 8)


if __name__ == "__main__":
    exit_code_1 = pytest.main(['-k', 'test_distance_int'])
    exit_code_2 = pytest.main(['-k', 'test_distance_float'])
    print(f'test_distance_int\t-\t{"TRUE" if not exit_code_1 else "FALSE"}')
    print(f'test_distance_float\t-\t{"TRUE" if not exit_code_2 else "FALSE"}')
