from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QMainWindow, QGraphicsTextItem, QGraphicsEllipseItem
from PyQt5.QtGui import QPen, QColor
from PyQt5.QtCore import Qt, QRectF, QTimer, QPointF, QEvent
import sys


class Algo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.points = []  # Список для хранения точек в логических координатах сетки
        self.init_ui()

    def init_ui(self):
        self.scene = QGraphicsScene(self)  # Создаем сцену для отрисовки сетки и элементов
        self.view = QGraphicsView(self.scene, self)  # Создаем виджета для просмотра сцены
        self.setCentralWidget(self.view)  # Установим виджета просмотра как центральный элемент в окне

        self.scene.setSceneRect(0, 0, 800, 600)  # Размер сцены

        self.base_point = [0, 0]  # Базовая точка для панорамирования и масштабирования
        self.grid_step = 50  # Шаг сетки

        self.timer = QTimer()  # Таймер для периодического обновления сетки (как раз те самые тики)
        self.timer.timeout.connect(self.draw_grid)
        self.timer.start(100)  # Обновление сетки каждые 100 мс

        self.setWindowTitle("Точно не GeoGebra v0.1.0")
        self.view.setFocusPolicy(Qt.StrongFocus)  # Установка фильтра событий для обработки кликов мыши
        self.view.viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress and source is self.view.viewport():
            point = self.view.mapToScene(event.pos())
            if event.button() == Qt.LeftButton:
                self.add_point(point)
            elif event.button() == Qt.RightButton:
                self.remove_point(point)
            return True
        return super().eventFilter(source, event)

    def draw_grid(self):
        self.scene.clear()  # Очищаем сцену перед перерисовкой

        pen = QPen(Qt.gray, 0.5)  # Создаем перо для рисования сетки
        rect = self.scene.sceneRect()  # Текущий размер сцены

        # Отрисовка вертикальных и горизонтальных линий сетки
        for x in range(int(rect.left()) - self.base_point[0] % self.grid_step, int(rect.right()), self.grid_step):
            self.scene.addLine(x, rect.top(), x, rect.bottom(), pen)
        for y in range(int(rect.top()) - self.base_point[1] % self.grid_step, int(rect.bottom()), self.grid_step):
            self.scene.addLine(rect.left(), y, rect.right(), y, pen)

        self.draw_axes()  # Отрисовка осей координат и точек
        self.draw_points()

    def draw_axes(self):
        axisPen = QPen(Qt.black, 2)  # Перо для рисования осей координат
        rect = self.scene.sceneRect()

        # X-axis
        self.scene.addLine(rect.left(), -self.base_point[1], rect.right(), -self.base_point[1], axisPen)
        # Y-axis
        self.scene.addLine(-self.base_point[0], rect.top(), -self.base_point[0], rect.bottom(), axisPen)

        self.add_axis_labels()  # Добавление подписей к осям

    def add_axis_labels(self):
        rect = self.scene.sceneRect()
        step = self.grid_step
        # Добавление подписей к вертикальным и горизонтальным линиям
        for x in range(int(rect.left()) - self.base_point[0] % step, int(rect.right()), step):
            if x != -self.base_point[0]:  # Избегаем перекрытия с осью Y
                label = QGraphicsTextItem(f"{(x + self.base_point[0]) // step}")
                label.setPos(x, -self.base_point[1])
                self.scene.addItem(label)
        for y in range(int(rect.top()) - self.base_point[1] % step, int(rect.bottom()), step):
            if y != -self.base_point[1]:  # И с осью X
                label = QGraphicsTextItem(f"{-(y + self.base_point[1]) // step}")
                label.setPos(-self.base_point[0], y)
                self.scene.addItem(label)

    def add_point(self, point):
        logicalX = (point.x() - self.view.width() / 2) / self.grid_step + self.base_point[0] / self.grid_step  # Преобразование экранных координат в логические координаты сетки (используем basePoint)
        logicalY = (point.y() - self.view.height() / 2) / self.grid_step + self.base_point[1] / self.grid_step
        print(logicalX, logicalY)
        self.points.append((logicalX, logicalY))  # Добавление точки в список
        # self.draw_grid()  # Перерисовка сетки c "новой" точки

    def remove_point(self, point):
        # Преобразование координат клика в логические координаты
        logicalX = (point.x() - self.view.width() / 2) / self.grid_step + self.base_point[0] / self.grid_step
        logicalY = (point.y() - self.view.height() / 2) / self.grid_step + self.base_point[1] / self.grid_step

        # Пороговое значение для определения "близости" точки
        tolerance = 0.1  # Может зависеть от масштаба сетки

        # Поиск точки в списке с учетом погрешности
        for p in self.points:
            if abs(p[0] - logicalX) < tolerance and abs(p[1] - logicalY) < tolerance:
                self.points.remove(p)
                break

        # self.draw_grid()

    def draw_points(self):
        radius = 3  # Радиус точек
        for logicalX, logicalY in self.points:
            screenX = (logicalX - self.base_point[0] / self.grid_step) * self.grid_step + self.view.width() / 2  # Преобразование логических координат в экранные
            screenY = (logicalY - self.base_point[1] / self.grid_step) * self.grid_step + self.view.height() / 2

            ellipse = QGraphicsEllipseItem(screenX - radius, screenY - radius, 2 * radius, 2 * radius)  # Рисуем точки на сцене
            ellipse.setBrush(QColor(Qt.red))
            self.scene.addItem(ellipse)

    def keyPressEvent(self, event):
        step = 10  # Шаг панорамирования
        zoom_factor = 10  # Шаг масштабирования

        if event.key() == Qt.Key_D:
            self.base_point[0] += step
        elif event.key() == Qt.Key_A:
            self.base_point[0] -= step
        elif event.key() == Qt.Key_W:
            self.base_point[1] -= step
        elif event.key() == Qt.Key_S:
            self.base_point[1] += step
        elif event.key() == Qt.Key_Equal:
            self.grid_step += zoom_factor
        elif event.key() == Qt.Key_Minus and self.grid_step > zoom_factor:
            self.grid_step -= zoom_factor
        else:
            super().keyPressEvent(event)
            return

        self.draw_grid()  # Перерисовываем сетку с учетом нового положения или масштаба (можно и без этого, но для большей плавности)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = Algo()
    mainWin.show()
    sys.exit(app.exec_())
