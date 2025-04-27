import pygame
import math
from settings import PLAYER_SPEED


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.original_image = pygame.image.load('assets/player.png').convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)
        self.speed = PLAYER_SPEED
        self.health = 100
        self.ammo = 10
        self.shooting = False
        self.shoot_cooldown = 250  # мс между выстрелами
        self.last_shot = pygame.time.get_ticks()

    def update(self, keys, mouse_pos):
        # Движение
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy = -self.speed
        if keys[pygame.K_s]: dy = self.speed
        if keys[pygame.K_a]: dx = -self.speed
        if keys[pygame.K_d]: dx = self.speed

        self.rect.x += dx
        self.rect.y += dy

        # Поворот за курсором
        self.rotate(mouse_pos)

        if self.shooting:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_cooldown:
                self.shoot()
                self.last_shot = now

    def rotate(self, mouse_pos):
        rel_x, rel_y = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        angle = (180 / math.pi) * -math.atan2(rel_y, rel_x)
        self.image = pygame.transform.rotate(self.original_image, int(angle))
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        if self.ammo > 0:
            self.ammo -= 1
            return True
        return False

    def draw_reload_indicator(self, screen):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_cooldown:
            font = pygame.font.Font(None, 30)
            text = font.render("Reloading...", True, (255, 0, 0))
            screen.blit(text, (10, 50))

