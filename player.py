import pygame
import math
from settings import PLAYER_SPEED
from bullet import Bullet

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
        self.shoot_cooldown = 250  # мс
        self.last_shot = pygame.time.get_ticks()
        self.reload_font = pygame.font.Font(None, 30)

    def update(self, keys, mouse_pos, bullets_group):
        self.handle_movement(keys)
        self.rotate(mouse_pos)
        self.handle_shooting(mouse_pos, bullets_group)

    def handle_movement(self, keys):
        dx = dy = 0
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed
        self.rect.x += dx
        self.rect.y += dy

    def rotate(self, mouse_pos):
        rel_x, rel_y = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        angle = math.degrees(-math.atan2(rel_y, rel_x))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def handle_shooting(self, mouse_pos, bullets_group):
        now = pygame.time.get_ticks()
        if self.shooting and now - self.last_shot > self.shoot_cooldown and self.ammo > 0:
            bullet = Bullet(self.rect.center, mouse_pos)
            bullets_group.add(bullet)
            self.ammo -= 1
            self.last_shot = now

    def draw_reload_indicator(self, screen):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_cooldown:
            text = self.reload_font.render("Reloading...", True, (255, 0, 0))
            screen.blit(text, (10, 70))
