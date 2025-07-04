import pygame


class Shop:
    def __init__(self):
        self.font = pygame.font.SysFont("arial", 24)
        self.shop_rect = pygame.Rect(200, 150, 400, 300)
        self.button_rect = pygame.Rect(300, 350, 200, 50)
        self.close_rect = pygame.Rect(560, 160, 30, 30)

    def handle_event(self, event, player):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos  # используем позицию клика из события, а не pygame.mouse.get_pos()
            if self.close_rect.collidepoint(mouse_pos):
                return 'close'  # сигнал для закрытия магазина
            if self.button_rect.collidepoint(mouse_pos) and player.coins >= 5:
                player.ammo += 10
                player.coins -= 5
        return None

    def draw(self, screen, player):
        mouse_pos = pygame.mouse.get_pos()

        # Затемнение поверх игрового экрана (оставляем игру видимой под ним)
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 0))  # прозрачное затемнение
        screen.blit(overlay, (0, 0))

        # Центрируем окно магазина на экране
        screen_rect = screen.get_rect()
        shop_width, shop_height = 400, 300
        self.shop_rect = pygame.Rect(0, 0, shop_width, shop_height)
        self.shop_rect.center = screen_rect.center

        # Обновляем расположение кнопок относительно нового shop_rect
        self.button_rect.topleft = (self.shop_rect.left + 100, self.shop_rect.top + 200)
        self.close_rect.topleft = (self.shop_rect.right - 40, self.shop_rect.top + 10)

        # Рисуем окно магазина
        pygame.draw.rect(screen, (50, 50, 50), self.shop_rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), self.shop_rect, 4, border_radius=8)

        # Кнопка закрытия (крестик)
        is_hover_close = self.close_rect.collidepoint(mouse_pos)
        close_color = (180, 20, 20) if is_hover_close else (255, 50, 50)
        pygame.draw.rect(screen, close_color, self.close_rect, border_radius=4)
        x_text = self.font.render("X", True, (255, 255, 255))
        screen.blit(x_text, (self.close_rect.x + 7, self.close_rect.y + 2))

        # Название
        title = self.font.render("МАГАЗИН", True, (255, 255, 0))
        screen.blit(title, (self.shop_rect.centerx - title.get_width() // 2, self.shop_rect.top + 20))

        # Инфо игрока
        coin_text = self.font.render(f"Монеты: {player.coins}", True, (255, 215, 0))
        ammo_text = self.font.render(f"Патроны: {player.ammo}", True, (255, 255, 255))
        screen.blit(coin_text, (self.shop_rect.centerx - coin_text.get_width() // 2, self.shop_rect.top + 70))
        screen.blit(ammo_text, (self.shop_rect.centerx - ammo_text.get_width() // 2, self.shop_rect.top + 110))

        # Кнопка покупки
        is_hover_btn = self.button_rect.collidepoint(mouse_pos)
        btn_color = (70, 70, 180) if is_hover_btn else (100, 100, 255)
        pygame.draw.rect(screen, btn_color, self.button_rect, border_radius=6)
        buy_text = self.font.render("Купить 10 патронов (5 монет)", True, (255, 255, 255))
        screen.blit(buy_text, (self.button_rect.centerx - buy_text.get_width() // 2,
                               self.button_rect.centery - buy_text.get_height() // 2))
