import json
from MathLab import game_rc

from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QWidget, QVBoxLayout, QLineEdit, QAction
from PyQt5.QtCore import Qt
from gui.custom_graphics_view import CustomGraphicsView
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QAction, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QSize, QTimer, QFile
from gui.custom_graphics_view import CustomGraphicsView
from gui.canvas import Canvas
from gui.dock_tools import DockTools
from core.geometric_objects.geom_obj import Point, Line, Segment, Ray, Info
from core.geometric_objects.figure import Circle, Polygon
from dlgselectmode import DlgSelectMode

default_size = [1200, 800]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.runGame = False
        self.fileName = None
        self.setWindowTitle("MathLab [*]")
        self.setMinimumSize(QSize(600, 400))
        self.setGeometry(100, 100, 1200, 800)
        self.initUI()
        self.initMenu()
        self.scene.shapes_manager.comm.shapesChanged.connect(self.onSceneChanged)

    def onTaskSelected(self, dlg):
        filename = ":/resources/" + dlg.currentFileName + ".json"
        print("Task Selected", filename)
        self.loadFile(filename)
        self.runGame = True

    def closeEvent(self, event):
        if self.confirmContinue():
            event.accept()
        else:
            event.ignore()
    def showEvent(self, event):
        self.selectMode()
        event.accept()

    def selectMode(self):
        if not self.confirmContinue():
            return
        dlg = DlgSelectMode()
        dlg.taskSelected.connect(self.onTaskSelected)

        if dlg.exec():
            self.modeGame = dlg.modeGame
            print("selected mode is ", self.modeGame)

        else:
            print("reject")

    def checkWin(self):
        return True

    def onSceneChanged(self):
        self.setWindowModified(True)
        if self.runGame == True:
            if self.checkWin():
                QMessageBox.information(self, "MathLab", "Победа ефыл ттт решена")
        pass

    def resizeEvent(self, event):
        new_size = event.size()  # получаем новый размер окна
        self.scene.setSceneRect(0, 0, new_size.width() - self.dockTools.width() - 2, new_size.height() - 2)
        self.view.setFixedSize(new_size.width() - self.dockTools.width(), new_size.height())
        self.scene.update_scene()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.scene = Canvas(self.width() - 200, self.height())

        self.view = CustomGraphicsView(self.scene)
        self.view.setFixedSize(1000, 800)

        self.layout.addWidget(self.view)
        self.dockTools = DockTools()

        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockTools)

        self.dockTools.set_active_tool("Move")
        self.dockTools.btn_add_ed_func.clicked.connect(self.on_add_ed_func)
        self.dockTools.connect_actions(self.tool_selected)

    def initMenu(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Файл')
        editMenu = menubar.addMenu('Редактировать')

        openAction = QAction('Открыть...', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.open)
        fileMenu.addAction(openAction)

        saveAction = QAction('Сохранить', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.save)
        fileMenu.addAction(saveAction)

        saveAsAction = QAction('Сохранить как...', self)
        saveAsAction.triggered.connect(self.saveAs)
        fileMenu.addAction(saveAsAction)

        fileMenu.addSeparator()

        selectModeAction = QAction('Выбрать режим...', self)
        selectModeAction.triggered.connect(self.selectMode)
        fileMenu.addAction(selectModeAction)

        fileMenu.addSeparator()

        exitAction = QAction('Выход', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)


    def onClose(self):
        self.confirmContinue()

    def confirmContinue(self):
        if not self.isWindowModified():
            return True
        res = QMessageBox.question(self, "MathLab", "Есть несохраненные изменения. Вы хотите продолжить?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if res == QMessageBox.Yes:
            return True
        return False

    def loadFile(self, fileName):
        inFile = QFile(fileName)
        if not inFile.open(QFile.ReadOnly | QFile.Text):
            QMessageBox.warning(self, "MathLab", "Не могу открыть файл %s\n%s" % (fileName, inFile.errorString()))
            return
        ba = inFile.readAll()
        inFile.close()
        root = json.loads(str(ba, 'utf-8'))
        self.readRoot(root)
        self.fileName = fileName
        self.setWindowModified(False)
        self.setWindowTitle("MathLab %s [*]" % self.fileName)

    def open(self):
        if not self.confirmContinue():
            return
        fileName, _ = QFileDialog.getOpenFileName(self, "Открыть файл MathLab", "", "*.json;;*.*")
        if fileName:
            self.loadFile(fileName)


    def readRoot(self, root):
        self.scene.base_point = root['saved_params']['base_point']
        self.scene.zoom_factor = root['saved_params']['zoom_factor']
        self.shapes_to_scene(root['saved_shapes'])
        self.scene.update_scene()

    def shapes_to_scene(self, saved_shapes):
        shapes = {Point: [], Segment: [], Polygon: [], Line: [], Ray: [], Circle: [], Info: []}

        for key in saved_shapes:
            if key == 'Points':
                for saved_point in saved_shapes[key]:
                    point = Point(saved_point['x'], saved_point['y'])
                    point.name = saved_point['name']
                    point.color = saved_point['color']
                    point.radius = saved_point['radius']
                    shapes[Point].append(point)

            if key == 'Segments':
                for saved_segment in saved_shapes[key]:
                    pnt = [Point(saved_segment['x1'], saved_segment['y1']), Point(saved_segment['x2'], saved_segment['y2'])]
                    segment = Segment(pnt, width=saved_segment['width'], color=saved_segment['color'])
                    shapes[Segment].append(segment)

            if key == 'Rays':
                for saved_ray in saved_shapes[key]:
                    pnt = [Point(saved_ray['x1'], saved_ray['y1']), Point(saved_ray['x2'], saved_ray['y2'])]
                    ray = Ray(pnt, width=saved_ray['width'], color=saved_ray['color'])
                    shapes[Ray].append(ray)

            if key == 'Circles':
                for saved_circle in saved_shapes[key]:
                    pnt = [Point(saved_circle['x1'], saved_circle['y1']), Point(saved_circle['x2'], saved_circle['y2'])]
                    circle = Circle(pnt, width=saved_circle['width'], color=saved_circle['color'])
                    shapes[Circle].append(circle)

            if key == 'Infos':
                for saved_info in saved_shapes[key]:
                    info = Info(x=saved_info['x'], y=saved_info['y'], message=saved_info['message'])
                    shapes[Info].append(info)

            if key == 'Polygons':
                for saved_polygon in saved_shapes[key]:
                    pnt = saved_polygon['points']
                    polygon = Polygon(pnt, color=saved_polygon['color'])
                    shapes[Polygon].append(polygon)

            if key == 'Lines':
                for saved_line in saved_shapes[key]:
                    pnt = [Point(saved_line['x1'], saved_line['y1']), Point(saved_line['x2'], saved_line['y2'])]
                    line = Line(pnt, width=saved_line['width'], color=saved_line['color'])
                    shapes[Line].append(line)

        self.scene.shapes_manager.shapes = shapes

    def save(self):
        if not self.fileName:
            self.saveAs()
        else:
            self.saveFile(self.fileName)

    def saveAs(self):
        fileName, _ = QFileDialog.getSaveFileName(self, "Сохранить файл MathLab", "", "*.json")
        if fileName:
            self.saveFile(fileName)

    def saveFile(self, fileName):
        with open(fileName, 'w', encoding='utf-8') as f:
            shapes = self.scene.shapes_manager.shapes

            zoom = self.scene.zoom_factor
            base = self.scene.base_point
            saved_params = {'zoom_factor': self.scene.zoom_factor, 'base_point': self.scene.base_point}

            saved_shapes = {}
            saved_shapes['Points'] = []
            saved_shapes['Lines'] = []
            saved_shapes['Segments'] = []
            saved_shapes['Rays'] = []
            saved_shapes['Circles'] = []
            saved_shapes['Polygons'] = []
            saved_shapes['Infos'] = []
            for key in shapes:
                for shape in shapes[key]:
                    if type(shape) == Point:
                        saved_shapes['Points'].append({'name': shape.name, 'color': shape.color, 'radius': shape.radius,
                                                       'x': shape.x, 'y': shape.y})
                    if type(shape) == Line:
                        saved_shapes['Lines'].append({'color': shape.color, 'width': shape.width,
                                                      'x1': shape.point_1.x, 'y1': shape.point_1.y,
                                                      'x2': shape.point_2.x, 'y2': shape.point_2.y})
                    if type(shape) == Segment:
                        saved_shapes['Segments'].append({'color': shape.color, 'width': shape.width,
                                                         'x1': shape.point_1.x, 'y1': shape.point_1.y,
                                                         'x2': shape.point_2.x, 'y2': shape.point_2.y})
                    if type(shape) == Ray:
                        saved_shapes['Rays'].append({'color': shape.color, 'width': shape.width,
                                                     'x1': shape.point_1.x, 'y1': shape.point_1.y,
                                                     'x2': shape.point_2.x, 'y2': shape.point_2.y})
                    if type(shape) == Circle:
                        saved_shapes['Circles'].append({'color': shape.color, 'width': shape.width,
                                                        'x1': shape.point_1.x, 'y1': shape.point_1.y,
                                                        'x2': shape.point_2.x, 'y2': shape.point_2.y})
                    if type(shape) == Info:
                        saved_shapes['Infos'].append({'message': shape.message, 'x': shape.x, 'y': shape.y})

                    if type(shape) == Polygon:
                        points_coords = []
                        for pnt in shape.points:
                            points_coords.append({'x': pnt.x, 'y': pnt.y})
                        saved_shapes['Polygons'].append({'color': shape.color, 'points': points_coords})

            root = {'saved_params': saved_params, 'saved_shapes': saved_shapes}
            json.dump(root, f, indent=4)
            self.fileName = fileName
            self.setWindowModified(False)
            self.setWindowTitle("MathLab %s [*]" % self.fileName)

    def on_add_ed_func(self):
        print("on_add_ed_func")
        # self.edFuncs = {}
        ed_and_btn = self.dockTools.add_ed_func()
        ed_and_btn['ed'].textChanged.connect(self.on_text_changed_ed_func)
        ed_and_btn['btn'].clicked.connect(self.on_del_ed_func)

    def find_index_ed_func(self, wgt, indexWgt):
        cnt = self.dockTools.layEdFuncs.count()
        for i in range(cnt):
            hlay = self.dockTools.layEdFuncs.itemAt(i)
            if hlay.itemAt(indexWgt).widget() == wgt:
                return i
        return -1

    def on_del_ed_func(self):
        btn = self.sender()
        num = self.find_index_ed_func(btn, 1)
        print(num, ": ")
        layItem = self.dockTools.layEdFuncs.itemAt(num)
        for i in range(layItem.count()):
            layItem.itemAt(i).widget().deleteLater()
        self.dockTools.layEdFuncs.removeItem(layItem)

    def on_text_changed_ed_func(self):
        ed = self.sender()
        num = self.find_index_ed_func(ed, 0)
        print(num, ": ", ed.text())

    def tool_selected(self, tool_name):
        self.view.current_tool = tool_name
