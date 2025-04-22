import pygame
import sys

from player import Player
from menu import WIDTH, HEIGHT, FPS, BLACK, display
from buttons import font
from map import Map
from camera import Camera

clock = pygame.time.Clock()

DEFAULT_BACKGROUND_COLOR = (24, 164, 86)
background_color = DEFAULT_BACKGROUND_COLOR  # Текущий цвет фона

bg_x = 0
bg_y = 0
in_game = False


def game_loop():
    global in_game  # Используем глобальную переменную

    # Загружаем карту
    try:
        game_map = Map('Maps/Card_game.tmx')  # Убедитесь, что путь правильный
    except Exception as e:
        print(f"Ошибка при загрузке карты: {e}")
        sys.exit()

    # Получаем размеры карты
    map_width = game_map.tmx_data.width * game_map.tile_size
    map_height = game_map.tmx_data.height * game_map.tile_size

    # Создаем игрока и камеру
    player = Player(400, 300, 32, 42, map_width, map_height)
    camera = Camera(WIDTH, HEIGHT, map_width, map_height)

    start_ticks = pygame.time.get_ticks()
    display.fill(DEFAULT_BACKGROUND_COLOR)

    while in_game:
        # Обновляем положение игрока
        player.handle_input()
        player.move()

        # Получаем состояние клавиш
        keys = pygame.key.get_pressed()

        # Получаем координаты мыши
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Обновляем смещение камеры с учётом координат мыши
        camera.update(player, mouse_x, mouse_y)

        # Очистка экрана
        display.fill(DEFAULT_BACKGROUND_COLOR)

        # Отрисовка карты с учетом смещения камеры
        game_map.draw(display, camera)

        # Отрисовка игрока
        player.draw(display, camera) # Исправлено количество аргументов
        pygame.display.update()

        # Таймер
        elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000
        timer_text = font.render(f"Time: {elapsed_time}s", True, BLACK)
        display.blit(timer_text, (10, 10))

        # Обновление экрана
        pygame.display.flip()
        clock.tick(FPS)

    # После выхода из игрового цикла корректно завершаем Pygame
    pygame.quit()
    sys.exit()


def start_new_game():
    global in_game
    in_game = True  # Меняем состояние на начало новой игры
    game_loop()  # Запускаем игровой цикл
