class DataManager:
    # Конструктор класса DataManager, инициализирует хранилище для точек
    def __init__(self):
        self.points = [] # Список для хранения точек

    # Метод для добавления новой точки в список
    def add_point(self, x, y):
        self.points.append((x, y))

    # Метод для получения списка всех добавленных точек
    def get_points(self):
        return self.points
