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

    def on_mouse_press(self, event):
        # Обработчик события нажатия мыши, добавляет точку и рисует её
        if event.inaxes:
            self.data_manager.add_point(event.xdata, event.ydata) # Добавление точки в менеджер данных
            self.draw_point(event.xdata, event.ydata) # Рисование точки

    def draw_point(self, x, y):
        # Метод для рисования точки на холсте
        self.ax.plot(x, y, 'ro') # Рисование красной точки
        self.draw() # Обновление холста для отображения нарисованной точки