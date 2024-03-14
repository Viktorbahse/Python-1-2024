from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt


class Canvas(QGraphicsScene):
    def __init__(self, parent=None, zoom_factor=1.0):
        super().__init__(parent)
        self.zoom_factor = zoom_factor
        self.grid_step = 50
        self.base_point = [0, 0]
        self.setSceneRect(0, 0, 800 - 2, 600 - 2)

    def to_logical_coords(self, scene_x, scene_y):
        center_x = self.sceneRect().width() / 2 + self.base_point[0]
        center_y = self.sceneRect().height() / 2 + self.base_point[1]
        logical_x = (scene_x - center_x) / self.zoom_factor
        logical_y = (center_y - scene_y) / self.zoom_factor
        return logical_x, logical_y

    def to_scene_coords(self, logical_x, logical_y):
        center_x = self.sceneRect().width() / 2 + self.base_point[0]
        center_y = self.sceneRect().height() / 2 + self.base_point[1]
        scene_x = logical_x * self.zoom_factor + center_x
        scene_y = center_y - logical_y * self.zoom_factor
        return scene_x, scene_y

    def set_zoom_factor(self, factor):
        self.zoom_factor = factor
        self.draw_grid()

    def draw_grid(self):
        self.clear()
        pen = QPen(Qt.gray, 0.5)
        step = self.grid_step

        width = self.sceneRect().width()
        height = self.sceneRect().height()

        left_logical = self.to_logical_coords(0, 0)[0]
        right_logical = self.to_logical_coords(width, height)[0]
        top_logical = self.to_logical_coords(0, 0)[1]
        bottom_logical = self.to_logical_coords(width, height)[1]

        x = left_logical - (left_logical % step)
        while x <= right_logical:
            x_scene, top_scene = self.to_scene_coords(x, top_logical)
            _, bottom_scene = self.to_scene_coords(x, bottom_logical)
            self.addLine(x_scene, top_scene, x_scene, bottom_scene, pen)
            x += step

        y = bottom_logical - (bottom_logical % step)
        while y <= top_logical:
            left_scene, y_scene = self.to_scene_coords(left_logical, y)
            right_scene, _ = self.to_scene_coords(right_logical, y)
            self.addLine(left_scene, y_scene, right_scene, y_scene, pen)
            y += step