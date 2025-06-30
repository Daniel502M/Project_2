import pygame
from settings import WIDTH, HEIGHT

def show_menu():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Меню игры")
    clock = pygame.time.Clock()

    # Загрузка изображений для кнопок
    start_button_img = pygame.image.load("assets/play.png")
    menu_button_img = pygame.image.load("assets/menu.png")
    exit_button_img = pygame.image.load("assets/exit.png")

    # Размеры кнопок
    start_button_width = 145
    start_button_height = 44
    exit_button_width = 133
    exit_button_height = 44
    menu_button_width = 157
    menu_button_height = 44

    # Координаты кнопок
    start_button_x = WIDTH // 2 - start_button_width // 2
    start_button_y = HEIGHT // 2 - 50
    exit_button_x = WIDTH // 2 - exit_button_width // 2
    exit_button_y = HEIGHT // 2 + 150
    menu_button_x = WIDTH // 2 - menu_button_width // 2
    menu_button_y = HEIGHT // 2 + 50  # Примерная координата для кнопки меню

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button_rect.collidepoint(mouse_pos):
                    return True
                elif exit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    return False
                elif menu_button_rect.collidepoint(mouse_pos):
                    # Здесь можно добавить логику для кнопки меню
                    pass

        screen.fill((207, 198, 184))
        #screen.fill((191, 121, 88))

        # Изменение размера изображений кнопок
        start_button_scaled = pygame.transform.scale(start_button_img, (start_button_width, start_button_height))
        exit_button_scaled = pygame.transform.scale(exit_button_img, (exit_button_width, exit_button_height))
        menu_button_scaled = pygame.transform.scale(menu_button_img, (menu_button_width, menu_button_height))

        # Отображение кнопок на экране
        start_button_rect = screen.blit(start_button_scaled, (start_button_x, start_button_y))
        exit_button_rect = screen.blit(exit_button_scaled, (exit_button_x, exit_button_y))
        menu_button_rect = screen.blit(menu_button_scaled, (menu_button_x, menu_button_y))

        pygame.display.flip()
        clock.tick(60)