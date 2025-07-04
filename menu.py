import pygame
from settings import WIDTH, HEIGHT

def show_menu():
    pygame.init()
    pygame.mouse.set_visible(True)  # <-- Добавь эту строку, чтобы курсор был виден в меню
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Меню игры")
    clock = pygame.time.Clock()

    # Загрузка изображений
    start_button_img = pygame.image.load("assets/play.png").convert_alpha()
    menu_button_img = pygame.image.load("assets/menu.png").convert_alpha()
    exit_button_img = pygame.image.load("assets/exit.png").convert_alpha()

    # Размеры кнопок
    start_button_size = (145, 44)
    menu_button_size = (157, 44)
    exit_button_size = (133, 44)

    # Масштабируем изображения
    start_button_img = pygame.transform.scale(start_button_img, start_button_size)
    menu_button_img = pygame.transform.scale(menu_button_img, menu_button_size)
    exit_button_img = pygame.transform.scale(exit_button_img, exit_button_size)

    # Получаем прямоугольники для размещения
    start_button_rect = start_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))
    menu_button_rect = menu_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
    exit_button_rect = exit_button_img.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if start_button_rect.collidepoint(mouse_pos):
                    return True
                elif menu_button_rect.collidepoint(mouse_pos):
                    # Здесь можно добавить функциональность меню (настройки и т.п.)
                    pass
                elif exit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    return False

        screen.fill((207, 198, 184))  # Цвет фона

        mouse_pos = pygame.mouse.get_pos()

        def draw_button(img, rect):
            if rect.collidepoint(mouse_pos):
                highlight = pygame.Surface(rect.size, pygame.SRCALPHA)
                highlight.fill((255, 255, 255, 40))
                screen.blit(img, rect.topleft)
                screen.blit(highlight, rect.topleft)
            else:
                screen.blit(img, rect.topleft)

        draw_button(start_button_img, start_button_rect)
        draw_button(menu_button_img, menu_button_rect)
        draw_button(exit_button_img, exit_button_rect)

        pygame.display.flip()
        clock.tick(60)
