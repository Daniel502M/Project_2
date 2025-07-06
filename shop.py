import pygame


class Shop:
    def __init__(self):
        self.font = pygame.font.SysFont("arial", 24)
        self.shop_rect = pygame.Rect(200, 150, 400, 300)
        self.ammo_button = pygame.Rect(0, 0, 250, 40)
        self.armor_button = pygame.Rect(0, 0, 250, 40)
        self.heal_button = pygame.Rect(0, 0, 250, 40)
        self.close_rect = pygame.Rect(560, 160, 30, 30)

    def handle_event(self, event, player):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.close_rect.collidepoint(mouse_pos):
                return 'close'

            # Покупка патронов
            if self.ammo_button.collidepoint(mouse_pos) and player.coins >= 5:
                player.ammo += 10
                player.coins -= 5

            # Покупка брони
            if self.armor_button.collidepoint(mouse_pos) and player.coins >= 10:
                player.armor += 50
                player.coins -= 10

            # Покупка аптечки
            if self.heal_button.collidepoint(mouse_pos) and player.coins >= 7:
                if player.health < player.max_health:
                    player.heal(30)
                    player.coins -= 7

        return None

    def draw(self, screen, player):
        mouse_pos = pygame.mouse.get_pos()

        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 0))
        screen.blit(overlay, (0, 0))

        screen_rect = screen.get_rect()
        shop_width, shop_height = 400, 350
        self.shop_rect = pygame.Rect(0, 0, shop_width, shop_height)
        self.shop_rect.center = screen_rect.center

        # Обновление координат кнопок
        self.ammo_button.topleft = (self.shop_rect.left + 75, self.shop_rect.top + 140)
        self.armor_button.topleft = (self.shop_rect.left + 75, self.shop_rect.top + 190)
        self.heal_button.topleft = (self.shop_rect.left + 75, self.shop_rect.top + 240)
        self.close_rect.topleft = (self.shop_rect.right - 40, self.shop_rect.top + 10)

        # Магазин
        pygame.draw.rect(screen, (50, 50, 50), self.shop_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), self.shop_rect, 4, border_radius=8)

        # Крестик
        is_hover_close = self.close_rect.collidepoint(mouse_pos)
        close_color = (180, 20, 20) if is_hover_close else (255, 50, 50)
        pygame.draw.rect(screen, close_color, self.close_rect, border_radius=4)
        x_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (self.close_rect.x + 7, self.close_rect.y + 2))

        # Заголовок
        title = self.font.render("МАГАЗИН", True, (255, 255, 0))
        screen.blit(title, (self.shop_rect.centerx - title.get_width() // 2, self.shop_rect.top + 20))

        # Инфо игрока
        coin_text = self.font.render(f"Монеты: {player.coins}", True, (255, 215, 0))
        ammo_text = self.font.render(f"Патроны: {player.ammo}", True, (255, 255, 255))
        health_text = self.font.render(f"Здоровье: {player.health}", True, (255, 0, 0))
        armor_text = self.font.render(f"Броня: {player.armor}", True, (100, 200, 255))

        screen.blit(coin_text, (self.shop_rect.centerx - coin_text.get_width() // 2, self.shop_rect.top + 70))
        screen.blit(ammo_text, (self.shop_rect.centerx - ammo_text.get_width() // 2, self.shop_rect.top + 100))
        screen.blit(health_text, (self.shop_rect.centerx - health_text.get_width() // 2, self.shop_rect.top + 125))
        screen.blit(armor_text, (self.shop_rect.centerx - armor_text.get_width() // 2, self.shop_rect.top + 150))

        # Кнопки покупки
        def draw_button(rect, text, hover_color, default_color):
            is_hover = rect.collidepoint(mouse_pos)
            color = hover_color if is_hover else default_color
            pygame.draw.rect(screen, color, rect, border_radius=6)
            text_surf = self.font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, (rect.centerx - text_surf.get_width() // 2,
                                    rect.centery - text_surf.get_height() // 2))

        draw_button(self.ammo_button, "Купить 10 патронов (5 монет)", (70, 70, 180), (100, 100, 255))
        draw_button(self.armor_button, "Купить броню (10 монет)", (50, 100, 200), (80, 120, 255))
        draw_button(self.heal_button, "Купить аптечку (7 монет)", (100, 180, 100), (100, 200, 100))
