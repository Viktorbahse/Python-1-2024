import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import FancyArrowPatch
# происходит рисование или отрисовка графики
# тут будут рисоваться геометрические фигуры, оси и т.п.


class Canvas(FigureCanvas):
    # Класс Canvas, интегрированного с Matplotlib, для рисования графики.
    # Инициализирует холст для рисования
    def __init__(self, data_manager, parent=None):
        fig, self.ax = plt.subplots(figsize=(5, 4), dpi=100) # Создание фигуры и осей для рисования.
        super().__init__(fig)
        self.setParent(parent)
        self.data_manager = data_manager
        self.drawing_mode = 'points'

        # Настройка осей и сетки для рисования (plt)
        self.ax.set_xlim([-10, 10])
        self.ax.set_ylim([-10, 10])
        self.ax.grid(True)

        # Вызов метода для рисования осей со стрелками (plt)
        self.draw_axes_with_arrows()

        # Подключение обработки событий нажатия мыши
        self.mpl_connect('button_press_event', self.on_mouse_press)


    def draw_axes_with_arrows(self):
        # Добавление стрелок на оси
        self.ax.add_patch(FancyArrowPatch((0, -10), (0, 10),
                                          arrowstyle='->', mutation_scale=10))
        self.ax.add_patch(FancyArrowPatch((-10, 0), (10, 0),
                                          arrowstyle='->', mutation_scale=10))

    def draw_point(self, x, y):
        # Метод для рисования точки на холсте
        self.ax.plot(x, y, 'ro') # Рисование красной точки
        self.draw() # Обновление холста для отображения нарисованной точки

    def on_mouse_press(self, event):
        # Обработчик события нажатия мыши, добавляет точку или линию в зависимости от режима
        if event.inaxes:
            if self.drawing_mode == 'points':
                # Режим добавления точек
                self.data_manager.add_point(event.xdata, event.ydata)
                self.draw_point(event.xdata, event.ydata)
            elif self.drawing_mode == 'lines':
                if hasattr(self, 'temp_line_start'):
                    # Фиксация линии
                    self.data_manager.add_line(self.temp_line_start, (event.xdata, event.ydata))
                    self.draw_line(self.temp_line_start, (event.xdata, event.ydata))
                    # Сброс состояния для новой линии
                    del self.temp_line_start
                    if hasattr(self, 'temp_line'):
                        self.temp_line.remove()
                        del self.temp_line
                    self.temp_line = None
                else:
                    # Если это первый клик, сохраняем начальную точку линии
                    self.temp_line_start = (event.xdata, event.ydata)

    def mouseMoveEvent(self, event):
        if hasattr(self, 'temp_line_start'):
            coords = self.ax.transData.inverted().transform((event.x(), event.y()))
            # print(coords)
            end_pos = (coords[0], self.ax.get_ylim()[1] - coords[1] + self.ax.get_ylim()[0])

            if self.temp_line is None:
                # Если temp_line ещё не создана, создаём её здесь
                self.temp_line, = self.ax.plot([self.temp_line_start[0], end_pos[0]],
                                               [self.temp_line_start[1], end_pos[1]], 'r--')
            else:
                # Если temp_line уже существует, обновляем её данные
                self.temp_line.set_data([self.temp_line_start[0], end_pos[0]],
                                        [self.temp_line_start[1], end_pos[1]])
            self.figure.canvas.draw_idle()

    def draw_line(self, start, end):
        # Рисует линию между двумя точками
        self.ax.plot([start[0], end[0]], [start[1], end[1]], 'r-')
        self.draw_idle()

    def pan(self, direction):
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        delta = 1  # Значение сдвига может быть адаптировано

        if direction == 'left':
            self.ax.set_xlim([xlim[0] - delta, xlim[1] - delta])
        elif direction == 'right':
            self.ax.set_xlim([xlim[0] + delta, xlim[1] + delta])
        elif direction == 'up':
            self.ax.set_ylim([ylim[0] + delta, ylim[1] + delta])
        elif direction == 'down':
            self.ax.set_ylim([ylim[0] - delta, ylim[1] - delta])

        self.draw()  # Обновление холста

    def setDrawingMode(self, mode):
        self.drawing_mode = mode
        if mode == 'lines':
            self.temp_line = None  # Временная линия для предварительного просмотра
