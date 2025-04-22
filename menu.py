import pygame
import sys

from buttons import Button, title_font

# Настройки экрана
WIDTH, HEIGHT = 800, 600
FPS = 60
display = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# background_image = pygame.image.load('./background_image.png').convert()

bg_speed = 2

# Цвета
DEFAULT_BACKGROUND_COLOR = (24, 164, 86)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

background_color = DEFAULT_BACKGROUND_COLOR  # Текущий цвет фона


def change_background_color(new_color):
    """
    Меняет цвет фона.
    """
    global background_color
    background_color = new_color


def main_menu():
    """
    Главное меню игры.
    """
    new_game_button = Button(300, 200, 200, 50, "New Game", lambda: "game")
    settings_button = Button(300, 280, 200, 50, "Settings", lambda: "settings")
    quit_button = Button(300, 360, 200, 50, "Quit", lambda: "quit")

    while True:
        display.fill(WHITE)

        menu_text = title_font.render("Main Menu", True, BLACK)
        menu_rect = menu_text.get_rect(center=(WIDTH // 2, 100))
        display.blit(menu_text, menu_rect)

        new_game_button.draw(display)
        settings_button.draw(display)
        quit_button.draw(display)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_game_button.is_hovered:
                    return new_game_button.action()
                elif settings_button.is_hovered:
                    return settings_button.action()
                elif quit_button.is_hovered:
                    return quit_button.action()

        pygame.display.flip()
        clock.tick(FPS)


def settings_menu():
    """
    Меню настроек игры.
    """
    red_button = Button(300, 200, 200, 50, "Red", lambda: change_background_color((255, 0, 0)))
    green_button = Button(300, 280, 200, 50, "Green", lambda: change_background_color((0, 255, 0)))
    blue_button = Button(300, 360, 200, 50, "Blue", lambda: change_background_color((0, 0, 255)))
    back_button = Button(300, 440, 200, 50, "Back to Menu", lambda: "menu")

    while True:
        display.fill(WHITE)

        settings_text = title_font.render("Settings", True, BLACK)
        settings_rect = settings_text.get_rect(center=(WIDTH // 2, 100))
        display.blit(settings_text, settings_rect)

        red_button.draw(display)
        green_button.draw(display)
        blue_button.draw(display)
        back_button.draw(display)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if red_button.is_hovered:
                    red_button.action()
                elif green_button.is_hovered:
                    green_button.action()
                elif blue_button.is_hovered:
                    blue_button.action()
                elif back_button.is_hovered:
                    return back_button.action()

        pygame.display.flip()
        clock.tick(FPS)


def pause_menu():
    global in_game
    in_game = False  # Останавливаем игровой цикл
    # После возврата управление должно перейти в main_menu или game_loop
    """
    Меню паузы игры.
    """
    continue_button = Button(300, 200, 200, 50, "Continue", lambda: "game")
    settings_button = Button(300, 280, 200, 50, "Settings", lambda: "settings")
    quit_button = Button(300, 360, 200, 50, "Quit to Menu", lambda: "menu")

    while True:
        display.fill(WHITE)

        pause_text = title_font.render("Paused", True, BLACK)
        pause_rect = pause_text.get_rect(center=(WIDTH // 2, 100))
        display.blit(pause_text, pause_rect)

        continue_button.draw(display)
        settings_button.draw(display)
        quit_button.draw(display)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if continue_button.is_hovered:
                    return continue_button.action()
                elif settings_button.is_hovered:
                    return settings_button.action()
                elif quit_button.is_hovered:
                    return quit_button.action()

        pygame.display.flip()
        clock.tick(FPS)
