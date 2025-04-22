import pygame

pygame.init()

WHITE = (255, 255, 255)

# Шрифты
font = pygame.font.Font(None, 36)
title_font = pygame.font.Font(None, 60)


class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.action = action
        self.is_hovered = False

    def draw(self, display):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.x <= mouse_x <= self.x + self.width and self.y <= mouse_y <= self.y + self.height:
            self.is_hovered = True
        else:
            self.is_hovered = False

        # Цвет кнопки в зависимости от наведения
        button_color = (0, 255, 0) if self.is_hovered else (0, 200, 0)
        pygame.draw.rect(display, button_color, (self.x, self.y, self.width, self.height))

        # Текст на кнопке
        text = font.render(self.text, True, WHITE)
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        display.blit(text, text_rect)

        # Если нажата кнопка
        if self.is_hovered and pygame.mouse.get_pressed()[0]:
            if self.action:
                self.action()

        # Если нажата кнопка
        if self.is_hovered and pygame.mouse.get_pressed()[0]:
            if self.action:
                self.action()