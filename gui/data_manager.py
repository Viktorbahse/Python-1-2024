class DataManager:
    # Конструктор класса DataManager, инициализирует хранилище для точек
    def __init__(self):
        self.points = [] # Список для хранения точек
        self.lines = []  # Добавляем список для хранения линий

    # Метод для добавления новой точки в список
    def add_point(self, x, y):
        self.points.append((x, y))

    # Метод для получения списка всех добавленных точек
    def get_points(self):
        return self.points

    def add_line(self, start, end):
        # Добавляет линию в список, где линия представлена как пара точек
        self.lines.append((start, end))

    def get_lines(self):
        # Возвращает список всех добавленных линий
        return self.lines
