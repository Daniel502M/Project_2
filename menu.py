import pygame
import sys
from settings import WIDTH, HEIGHT

selected_map_path = None  # <- сохраняем выбор карты глобально


def show_menu():
    global selected_map_path

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Zombie Game - Menu")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    maps = [
        {"name": "Laboratory", "file": "Maps/Laboratory_Cart/Laboratory_Cart.tmx"},
        {"name": "Lawn", "file": "Maps/Lawn_Cart/Lawn_Cart.tmx"}
    ]
    selected_map_index = 0

    # Загрузка изображений кнопок
    start_button_img = pygame.image.load("assets/play.png").convert_alpha()
    menu_button_img = pygame.image.load("assets/menu.png").convert_alpha()
    exit_button_img = pygame.image.load("assets/exit.png").convert_alpha()

    play_rect = start_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
    menu_rect = menu_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
    exit_rect = exit_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))

    map_buttons = []
    map_button_height = 60
    for i, m in enumerate(maps):
        rect = pygame.Rect(20, 30 + i * (map_button_height + 10), 180, map_button_height)
        map_buttons.append((rect, m))

    pygame.mouse.set_visible(True)

    while True:
        screen.fill((207, 198, 184))
        mouse_pos = pygame.mouse.get_pos()

        # Заголовок
        title = font.render("Zombie Game", True, (0, 0, 0))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Кнопки карт
        map_title = pygame.font.SysFont(None, 36).render("Карта:", True, (0, 0, 0))
        screen.blit(map_title, (20, 0))
        for i, (rect, m) in enumerate(map_buttons):
            is_selected = (i == selected_map_index)
            color = (0, 200, 0) if is_selected else (60, 60, 60)
            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2, border_radius=6)
            name_text = pygame.font.SysFont(None, 32).render(m["name"], True, (255, 255, 255))
            screen.blit(name_text, (rect.centerx - name_text.get_width() // 2, rect.centery - name_text.get_height() // 2))

        # Кнопки Play / Menu / Exit
        screen.blit(start_button_img, play_rect.topleft)
        screen.blit(menu_button_img, menu_rect.topleft)
        screen.blit(exit_button_img, exit_rect.topleft)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if play_rect.collidepoint(mouse_pos):
                    selected_map_path = maps[selected_map_index]["file"]
                    return "play"
                elif exit_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
                elif menu_rect.collidepoint(mouse_pos):
                    print("Menu button clicked")  # можешь тут добавить нужное поведение
                else:
                    for i, (rect, _) in enumerate(map_buttons):
                        if rect.collidepoint(mouse_pos):
                            selected_map_index = i

        pygame.display.flip()
        clock.tick(60)


def get_selected_map():
    return selected_map_path
