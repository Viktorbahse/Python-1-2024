from PyQt5.QtWidgets import QGraphicsView
from PyQt5.QtCore import Qt


class CustomGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        scene_pos = self.mapToScene(event.pos())
        logical_pos = self.scene().to_logical_coords(scene_pos.x(), scene_pos.y())
        self.scene().draw_grid()
        print(f"Logical coordinates: {logical_pos}")

    def keyPressEvent(self, event):
        step = 10
        if event.key() == Qt.Key_Equal:
            self.scene().zoom_factor *= 1.1
        if event.key() == Qt.Key_Minus:
            self.scene().zoom_factor /= 1.1
            self.scene().draw_grid()
        if event.key() == Qt.Key_W:
            self.scene().base_point[1] -= step
        elif event.key() == Qt.Key_S:
            self.scene().base_point[1] += step
        elif event.key() == Qt.Key_A:
            self.scene().base_point[0] -= step
        elif event.key() == Qt.Key_D:
            self.scene().base_point[0] += step

        self.scene().draw_grid()
        super().keyPressEvent(event)
