import pygame


class Camera:
    def __init__(self, width, height, map_width, map_height):
        self.width = width
        self.height = height
        self.offset_x = 0
        self.offset_y = 0
        self.map_width = map_width
        self.map_height = map_height

    def update(self, player, mouse_x, mouse_y):
        """Обновляем смещение камеры в зависимости от нажатых клавиш и положения курсора."""
        speed = 5  # Скорость движения камеры
        edge_margin = 30  # Граница экрана, у которой активируется движение камеры

        """Центрирует камеру на персонаже."""
        self.offset_x = player.x - self.width // 2
        self.offset_y = player.y - self.height // 2
        # Движение камеры с помощью курсора
        if mouse_x <= edge_margin:  # Курсор у левого края
            self.offset_x -= speed
        elif mouse_x >= self.width - edge_margin:  # Курсор у правого края
            self.offset_x += speed
        if mouse_y <= edge_margin:  # Курсор у верхнего края
            self.offset_y -= speed
        elif mouse_y >= self.height - edge_margin:  # Курсор у нижнего края
            self.offset_y += speed

        # Ограничиваем смещение камеры, чтобы она не выходила за границы карты
        self.offset_x = max(0, min(self.offset_x, self.map_width - self.width))
        self.offset_y = max(0, min(self.offset_y, self.map_height - self.height))

    def apply(self, rect):
        """Смещает объект относительно камеры."""
        return pygame.Rect(rect.x - self.offset_x, rect.y - self.offset_y, rect.width, rect.height)
