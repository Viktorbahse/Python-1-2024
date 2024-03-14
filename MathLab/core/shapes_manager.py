class ShapesManager:
    def __init__(self):
        self.shapes = []  # Список для хранения фигур
        self.temp_items = []  # Список для хранения временных фигур, таких как "предпросмотр"

    def add_shape(self, shape):
        self.shapes.append(shape)

    def remove_shape(self, shape):
        if shape in self.shapes:
            self.shapes.remove(shape)

    def find_shape(self, x, y, radius=5):
        for shape in self.shapes:
            if shape.contains_point(x, y, radius):
                return shape
        return

    def add_temp_line(self, shape):
        self.temp_items.append(shape)

    def clear_temp_lines(self):
        self.temp_items = []
