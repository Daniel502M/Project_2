import pygame


class Shop:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 36)
        self.large_font = pygame.font.SysFont(None, 48)
        self.ammo_cost = 3
        self.button_rect = pygame.Rect(0, 0, 200, 60)
        self.button_rect.center = (screen.get_width() // 2, screen.get_height() // 2 + 60)
        self.button_color = (60, 180, 75)
        self.button_hover_color = (100, 220, 100)
        self.bg_color = (20, 20, 20, 220)  # RGBA
        self.is_open = True

    def draw(self, screen, player):
        shop_bg = pygame.Surface((400, 300))
        shop_bg.fill((20, 20, 20))
        pygame.draw.rect(shop_bg, (255, 255, 255), (0, 0, 400, 300), 4)

        title = self.font.render("Магазин", True, (255, 255, 0))
        shop_bg.blit(title, (150, 20))

        # Кнопка покупки патронов
        pygame.draw.rect(shop_bg, (100, 100, 255), (100, 200, 200, 50))
        buy_text = self.font.render("Купить 10 патронов (5 монет)", True, (255, 255, 255))
        shop_bg.blit(buy_text, (105, 215))

        # Отображение количества монет игрока
        coin_text = self.font.render(f"Монеты: {player.coins}", True, (255, 215, 0))
        shop_bg.blit(coin_text, (140, 150))

        screen.blit(shop_bg, (screen.get_width() // 2 - 200, screen.get_height() // 2 - 150))

    def handle_event(self, event, player):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                if player.coins >= self.ammo_cost:
                    player.coins -= self.ammo_cost
                    player.ammo += 10

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.is_open = False
