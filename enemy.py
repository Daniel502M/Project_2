import pygame
import math
import random
from settings import ENEMY_SPEED, MAP_WIDTH, MAP_HEIGHT


class Enemy(pygame.sprite.Sprite):
    def __init__(self, target_pos):
        super().__init__()
        enemy_image_original = pygame.image.load("assets/enemy.png").convert_alpha()
        self.original_image = pygame.transform.scale(enemy_image_original, (60, 60))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=random_spawn_position())
        self.speed = ENEMY_SPEED
        self.health = 25

        # ==== НАСТРАИВАЕМЫЙ ХИТБОКС ====
        self.hitbox_width = int(self.rect.width * 0.3)
        self.hitbox_height = int(self.rect.height * 0.5)
        self.hitbox = pygame.Rect(0, 0, self.hitbox_width, self.hitbox_height)
        self.update_hitbox()

    def update(self, player_rect, obstacles):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        dx = dx / dist * self.speed
        dy = dy / dist * self.speed

        # === Движение по X с проверкой ===
        original_x = self.rect.x
        self.rect.x += dx
        self.update_hitbox()
        collision_x = any(self.hitbox.colliderect(obstacle) for obstacle in obstacles)
        if collision_x:
            self.rect.x = original_x
            self.update_hitbox()

        # === Движение по Y с проверкой ===
        original_y = self.rect.y
        self.rect.y += dy
        self.update_hitbox()
        collision_y = any(self.hitbox.colliderect(obstacle) for obstacle in obstacles)
        if collision_y:
            self.rect.y = original_y
            self.update_hitbox()

        # === Ограничения карты ===
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > MAP_WIDTH: self.rect.right = MAP_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > MAP_HEIGHT: self.rect.bottom = MAP_HEIGHT
        self.update_hitbox()

        # === Поворот изображения к игроку ===
        direction = pygame.Vector2(player_rect.center) - pygame.Vector2(self.rect.center)
        angle = math.degrees(-math.atan2(direction.y, direction.x)) + 90
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def draw_collision_rect(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)  # Только красный хитбокс


def random_spawn_position():
    edge = random.choice(['top', 'bottom', 'left', 'right'])
    if edge == 'top':
        return random.randint(0, MAP_WIDTH), -60
    elif edge == 'bottom':
        return random.randint(0, MAP_WIDTH), MAP_HEIGHT + 60
    elif edge == 'left':
        return -60, random.randint(0, MAP_HEIGHT)
    elif edge == 'right':
        return MAP_WIDTH + 60, random.randint(0, MAP_HEIGHT)
