import json
from MathLab import game_rc
# from sympy.parsing.sympy_parser import parse_expr
from PyQt5.QtWidgets import QMainWindow, QGraphicsScene, QWidget, QVBoxLayout, QLineEdit, QAction, QLabel
from PyQt5.QtCore import Qt
from gui.custom_graphics_view import CustomGraphicsView
from sympy import sympify
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QMessageBox, QAction
from PyQt5.QtCore import Qt, QSize, QTimer, QFile
from gui.canvas import Canvas
from gui.dock_tools import DockTools
from gui.timing_widget import TimingWidget
from gui.redo_undo_buttons import *
from tests.timing import *
from gui.uploading_downloading_files import *
from core.geometric_objects.figure import *
from core.geometric_objects.geom_obj import Point, Line, Segment, Ray, Info
from dlgselectmode import DlgSelectMode

from gui.authorization_interface import *

default_size = [1200, 800]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.runGame = False
        self.fileName = None
        self.setWindowTitle("MathLab [*]")
        self.setMinimumSize(QSize(600, 400))
        self.setGeometry(100, 100, 1200, 800)

        self.uploading_downloading_files = None
        self.display_timing = False  # Включает показ времени, за которое работает та или иная функция
        self.authorization = None
        self.registration = None
        self.log_out_widget = None
        self.is_authorized = False
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
        self.dockTools.btnAddEdFunc.clicked.connect(self.onAddEdFunc)
        self.dockTools.connect_actions(self.tool_selected)

        home_button = UndoRedoButton(parent=self, view=self.view, command="undo")
        home_button.move(260, 70)
        redo_button = UndoRedoButton(parent=self, view=self.view, command="redo")
        redo_button.move(360, 70)
        self.profile_button = ProfileButton(parent=self, view=self.view)
        self.profile_button.move(self.width() - 70, 50)

        if self.display_timing:  # Текст с временем работы функции
            self.init_timing_widget()

    def initMenu(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Файл')
        editMenu = menubar.addMenu('Редактировать')

        serverAction = QAction('Сервер', self)
        serverAction.triggered.connect(self.open_uploading_downloading_files)  # Связываем действие с методом
        menubar.addAction(serverAction)

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
        Authorization = QAction('Войти', self)
        Authorization.triggered.connect(self.open_authorization)
        menubar.addAction(Authorization)


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
        print('start shapes_to_scene')
        shapes = {Point: [], Segment: [], Polygon: [], Line: [], Ray: [], Circle: [], Info: [], Function: []}
        array_shapes = []
        for key in saved_shapes:
            if key == 'Points':
                for saved_point in saved_shapes[key]:
                    point = Point(sympify(saved_point['x']), sympify(saved_point['y']))
                    point.name = saved_point['name']
                    point.uid = saved_point['uid']
                    point.typeShape = saved_point['typeShape']
                    point.color = saved_point['color']
                    point.point_color = saved_point['point_color']
                    point.line_color = saved_point['line_color']
                    point.radius = saved_point['radius']
                    point.width = saved_point['width']
                    point.invisible = saved_point['invisible']
                    point.temp_owner = saved_point['owner']
                    point.temp_primary = saved_point['primary_elements']
                    point.temp_secondary = saved_point['secondary_elements']
                    point.temp_connected_shapes = saved_point['connected_shapes']
                    shapes[Point].append(point)
                    array_shapes.append(point)
                    print('array_shapes append point', point.uid)

            if key == 'Segments':
                for saved_segment in saved_shapes[key]:
                    pnt = [Point(sympify(saved_segment['x1']), sympify(saved_segment['y1'])),
                           Point(sympify(saved_segment['x2']), sympify(saved_segment['y2']))]
                    segment = Segment(pnt, width=saved_segment['width'], color=saved_segment['color'])
                    segment.primary_elements = []
                    segment.uid = saved_segment['uid']
                    segment.typeShape = saved_segment['typeShape']
                    segment.color = saved_segment['color']
                    segment.point_color = saved_segment['point_color']
                    segment.width = saved_segment['width']
                    segment.invisible = saved_segment['invisible']
                    segment.temp_owner = saved_segment['owner']
                    segment.temp_primary = saved_segment['primary_elements']
                    segment.temp_secondary = saved_segment['secondary_elements']
                    shapes[Segment].append(segment)
                    array_shapes.append(segment)
                    print('array_shapes append segment', segment.uid)

            if key == 'Rays':
                for saved_ray in saved_shapes[key]:
                    pnt = [Point(sympify(saved_ray['x1']), sympify(saved_ray['y1'])),
                           Point(sympify(saved_ray['x2']), sympify(saved_ray['y2']))]
                    ray = Ray(pnt, width=saved_ray['width'], color=saved_ray['color'])
                    ray.primary_elements = []
                    ray.uid = saved_ray['uid']
                    ray.typeShape = saved_ray['typeShape']
                    ray.color = saved_ray['color']
                    ray.point_color = saved_ray['point_color']
                    ray.width = saved_ray['width']
                    ray.invisible = saved_ray['invisible']
                    ray.temp_owner = saved_ray['owner']
                    ray.temp_primary = saved_ray['primary_elements']
                    ray.temp_secondary = saved_ray['secondary_elements']
                    shapes[Ray].append(ray)
                    array_shapes.append(ray)
                    print('array_shapes append ray', ray.uid)

            if key == 'Circles':
                for saved_circle in saved_shapes[key]:
                    pnt = [Point(sympify(saved_circle['x1']), sympify(saved_circle['y1'])),
                           Point(sympify(saved_circle['x2']), sympify(saved_circle['y2']))]
                    circle = Circle(pnt, width=saved_circle['width'], color=saved_circle['color'])
                    circle.primary_elements = []
                    circle.uid = saved_circle['uid']
                    circle.typeShape = saved_circle['typeShape']
                    circle.color = saved_circle['color']
                    circle.point_color = saved_circle['point_color']
                    circle.width = saved_circle['width']
                    circle.invisible = saved_circle['invisible']
                    circle.temp_owner = saved_circle['owner']
                    circle.temp_primary = saved_circle['primary_elements']
                    circle.temp_secondary = saved_circle['secondary_elements']
                    shapes[Circle].append(circle)
                    array_shapes.append(circle)
                    print('array_shapes append circle', circle.uid)

            if key == 'Infos':
                for saved_info in saved_shapes[key]:
                    info = Info(x=sympify(saved_info['x']), y=sympify(saved_info['y']), message=saved_info['message'])
                    shapes[Info].append(info)

            if key == 'Polygons':
                for saved_polygon in saved_shapes[key]:
                    pnt = saved_polygon['points']
                    polygon = Polygon(pnt, color=saved_polygon['color'])
                    shapes[Polygon].append(polygon)

            if key == 'Lines':
                for saved_line in saved_shapes[key]:
                    pnt = [Point(sympify(saved_line['x1']), sympify(saved_line['y1'])),
                           Point(sympify(saved_line['x2']), sympify(saved_line['y2']))]
                    line = Line(pnt, width=saved_line['width'], color=saved_line['color'])
                    line.primary_elements = []
                    line.uid = saved_line['uid']
                    line.typeShape = saved_line['typeShape']
                    line.color = saved_line['color']
                    line.point_color = saved_line['point_color']
                    line.width = saved_line['width']
                    line.invisible = saved_line['invisible']
                    line.temp_owner = saved_line['owner']
                    line.temp_primary = saved_line['primary_elements']
                    line.temp_secondary = saved_line['secondary_elements']
                    shapes[Line].append(line)
                    array_shapes.append(line)
                    print('array_shapes append line', line.uid)

            if key == 'Functions':
                pass

        self.correct(array_shapes)
        self.scene.shapes_manager.shapes = shapes
    def correct(self, array_shapes):
        for shape in array_shapes:
            if shape.typeShape:
                for obj in shape.temp_owner:
                    found_shape = self.find_shape_by_uid(obj['uid'], array_shapes)
                    if found_shape:
                        shape.owner.append(found_shape)
                    else:
                        print("Файл содержит некорректные данные")

                for obj in shape.temp_primary:
                    found_shape = self.find_shape_by_uid(obj['uid'], array_shapes)
                    if found_shape:
                        shape.primary_elements.append(found_shape)
                    else:
                        print("Файл содержит некорректные данные")

                for obj in shape.temp_secondary:
                    found_shape = self.find_shape_by_uid(obj['uid'], array_shapes)
                    if found_shape:
                        shape.secondary_elements.append(found_shape)
                    else:
                        print("Файл содержит некорректные данные")
                if shape.typeShape == 'Point':
                    for obj in shape.connected_shapes:
                        found_shape = self.find_shape_by_uid(obj['uid'], array_shapes)
                        if found_shape:
                            shape.connected_shapes.append(found_shape)
                        else:
                            print("Файл содержит некорректные данные")

    def find_shape_by_uid(self, uid, array_shapes):
        for shape in array_shapes:
            if shape.uid == uid:
                return shape
        return None

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
            saved_shapes['Functions'] = []
            for key in shapes:
                for shape in shapes[key]:
                    if type(shape) == Point:
                        obj_params = {'name': shape.name, 'color': shape.color,
                                                       'uid': shape.uid, 'typeShape': shape.typeShape,
                                                       'point_color': shape.point_color,
                                                       'line_color': shape.line_color,
                                                       'radius': shape.radius,
                                                       'x': str(shape.entity.x), 'y': str(shape.entity.y),
                                                       'invisible': shape.invisible, 'width': shape.width}
                        owner_params = []
                        for sh in shape.owner:
                            owner_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        primary_params = []
                        for sh in shape.primary_elements:
                            primary_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        secondary_params = []
                        for sh in shape.secondary_elements:
                            secondary_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        connected_params = []
                        for sh in shape.connected_shapes:
                            connected_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        obj_params['owner'] = owner_params
                        obj_params['primary_elements'] = primary_params
                        obj_params['secondary_elements'] = secondary_params
                        obj_params['connected_shapes'] = connected_params
                        saved_shapes['Points'].append(obj_params)
                    if type(shape) == Line:
                        obj_params = {'color': shape.color, 'width': shape.width,
                                                      'x1': str(shape.primary_elements[0].entity.x), 'y1': str(shape.primary_elements[0].entity.y),
                                                      'x2': str(shape.primary_elements[1].entity.x), 'y2': str(shape.primary_elements[1].entity.y),
                                                      'uid': shape.uid, 'typeShape': shape.typeShape,
                                                      'invisible': shape.invisible, 'point_color': shape.point_color}
                        owner_params = []
                        for sh in shape.owner:
                            owner_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        primary_params = []
                        for sh in shape.primary_elements:
                            primary_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        secondary_params = []
                        for sh in shape.secondary_elements:
                            secondary_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        obj_params['owner'] = owner_params
                        obj_params['primary_elements'] = primary_params
                        obj_params['secondary_elements'] = secondary_params
                        saved_shapes['Lines'].append(obj_params)

                    if type(shape) == Segment:
                        obj_params = {'color': shape.color, 'width': shape.width,
                                      'x1': str(shape.primary_elements[0].entity.x), 'y1': str(shape.primary_elements[0].entity.y),
                                      'x2': str(shape.primary_elements[1].entity.x), 'y2': str(shape.primary_elements[1].entity.y),
                                      'invisible': shape.invisible, 'point_color': shape.point_color,
                                      'uid': shape.uid, 'typeShape': shape.typeShape}
                        owner_params = []
                        for sh in shape.owner:
                            owner_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        primary_params = []
                        for sh in shape.primary_elements:
                            primary_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        secondary_params = []
                        for sh in shape.secondary_elements:
                            secondary_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        obj_params['owner'] = owner_params
                        obj_params['primary_elements'] = primary_params
                        obj_params['secondary_elements'] = secondary_params
                        saved_shapes['Segments'].append(obj_params)
                    if type(shape) == Ray:
                        obj_params = {'color': shape.color, 'width': shape.width,
                                      'x1': str(shape.primary_elements[0].entity.x), 'y1': str(shape.primary_elements[0].entity.y),
                                      'x2': str(shape.primary_elements[1].entity.x), 'y2': str(shape.primary_elements[1].entity.y),
                                      'invisible': shape.invisible, 'point_color': shape.point_color,
                                      'uid': shape.uid, 'typeShape': shape.typeShape}
                        owner_params = []
                        for sh in shape.owner:
                            owner_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        primary_params = []
                        for sh in shape.primary_elements:
                            primary_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        secondary_params = []
                        for sh in shape.secondary_elements:
                            secondary_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        obj_params['owner'] = owner_params
                        obj_params['primary_elements'] = primary_params
                        obj_params['secondary_elements'] = secondary_params
                        saved_shapes['Rays'].append(obj_params)
                    if type(shape) == Circle:
                        obj_params = {'color': shape.color, 'width': shape.width,
                                      'x1': str(shape.primary_elements[0].entity.x), 'y1': str(shape.primary_elements[0].entity.y),
                                      'x2': str(shape.primary_elements[1].entity.x), 'y2': str(shape.primary_elements[1].entity.y),
                                      'invisible': shape.invisible, 'point_color': shape.point_color,
                                      'uid': shape.uid, 'typeShape': shape.typeShape}
                        owner_params = []
                        for sh in shape.owner:
                            owner_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        primary_params = []
                        for sh in shape.primary_elements:
                            primary_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        secondary_params = []
                        for sh in shape.secondary_elements:
                            secondary_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        obj_params['owner'] = owner_params
                        obj_params['primary_elements'] = primary_params
                        obj_params['secondary_elements'] = secondary_params
                        saved_shapes['Circles'].append(obj_params)
                    if type(shape) == Info:
                        saved_shapes['Infos'].append({'message': shape.message, 'x': str(shape.x), 'y': str(shape.y)})

                    if type(shape) == Polygon:
                        obj_params = {'color': shape.color, 'width': shape.width, 'points': shape.points,
                                      'invisible': shape.invisible, 'point_color': shape.point_color,
                                      'line_color': shape.line_color, 'uid': shape.uid, 'typeShape': shape.typeShape}
                        owner_params = []
                        for sh in shape.owner:
                            owner_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        primary_params = []
                        for sh in shape.primary_elements:
                            primary_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        secondary_params = []
                        for sh in shape.secondary_elements:
                            secondary_params.append({'typeShape': sh.typeShape, 'uid': sh.uid})
                        obj_params['owner'] = owner_params
                        obj_params['primary_elements'] = primary_params
                        obj_params['secondary_elements'] = secondary_params
                        points_coords = []
                        for pnt in shape.points:
                            points_coords.append({'x': str(pnt.entity.x), 'y': str(pnt.entity.y)})
                        obj_params['points'] = points_coords
                        saved_shapes['Polygons'].append(obj_params)

                    if type(shape) == Function:
                        pass

            root = {'saved_params': saved_params, 'saved_shapes': saved_shapes}
            json.dump(root, f, indent=4)
            self.fileName = fileName
            self.setWindowModified(False)
            self.setWindowTitle("MathLab %s [*]" % self.fileName)

    def init_timing_widget(self):
        # Создает текст, где показывается время работы функции
        self.timing_widget = TimingWidget(self)
        self.timing_widget.move(230, 45)
        self.timing_widget.resize(200, 20)
        TIMING_SIGNAL.time_updated.connect(self.timing_widget.setText)

    def open_uploading_downloading_files(self):
        if not self.uploading_downloading_files:
            self.uploading_downloading_files = UploadingDownloadingFiles()  # Создаем окно только, если оно еще не создано
        self.uploading_downloading_files.show()

    def open_reg(self):
        self.authorization.close()
        if not self.registration:
            self.registration = Registration_interface(window=self)
        self.registration.show()

    def log_out_open_widget(self):
        if not self.log_out_widget:
            self.log_out_widget = ExitConfirmationWidget(mainwindow=self)
        self.log_out_widget.show()

    def log_out(self, flag):
        self.log_out_widget.close()
        self.log_out_widget = None
        if flag:
            self.is_authorized = False
            self.profile_button.setText("😐")

    def open_authorization(self):
        if not self.authorization:
            self.authorization = Log_in_interface(window=self)
            self.authorization.log_in_ui.pushButton_sign_up.clicked.connect(self.open_reg)
        self.authorization.show()

    def successful_authorization(self):
        self.is_authorized = True
        self.profile_button.setText("😉")
        self.authorization.close()
        self.authorization = None

    def successful_registration(self):
        self.registration.close()
        self.registration = None
        self.open_authorization()

    def onAddEdFunc(self):
        # self.edFuncs = {}
        self.scene.shapes_manager.functions.append(Function())
        edAndBtn = self.dockTools.addEdFunc()
        edAndBtn['ed'].textChanged.connect(self.onTextChangedEdFunc)
        edAndBtn['btn'].clicked.connect(self.onDelEdFunc)

    def findIndexEdFunc(self, wgt, indexWgt):
        cnt = self.dockTools.layEdFuncs.count()
        for i in range(cnt):
            hlay = self.dockTools.layEdFuncs.itemAt(i)
            if hlay.itemAt(indexWgt).widget() == wgt:
                return i
        return -1

    def onDelEdFunc(self):
        btn = self.sender()
        num = self.findIndexEdFunc(btn, 1)
        del self.scene.shapes_manager.functions[num]
        layItem = self.dockTools.layEdFuncs.itemAt(num)
        for i in range(layItem.count()):
            layItem.itemAt(i).widget().deleteLater()
        self.dockTools.layEdFuncs.removeItem(layItem)

    def onTextChangedEdFunc(self):
        ed = self.sender()
        num = self.findIndexEdFunc(ed, 0)
        self.scene.shapes_manager.functions[num].reset(ed.text().lower())  # Обновляем функцию.
        self.view.scene().update_scene()
        # self.scene.shapes_manager.resolve_intersections()  # Обновляем точки пересечения функций.

    def tool_selected(self, tool_name):
        self.view.current_tool = tool_name
