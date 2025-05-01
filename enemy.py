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
        self.rect = self.image.get_rect(center=(random_spawn_position()))
        self.speed = ENEMY_SPEED
        self.health = 25

    def update(self, player_rect, obstacles):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist == 0:
            return  # чтобы избежать деления на ноль

        dx, dy = dx / dist, dy / dist  # нормализация
        dx *= self.speed
        dy *= self.speed

        # Перемещение по X
        self.rect.x += dx
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if dx > 0:
                    self.rect.right = obstacle.left
                elif dx < 0:
                    self.rect.left = obstacle.right

        # Перемещение по Y
        self.rect.y += dy
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if dy > 0:
                    self.rect.bottom = obstacle.top
                elif dy < 0:
                    self.rect.top = obstacle.bottom

        # Ограничение в пределах карты
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > MAP_WIDTH:
            self.rect.right = MAP_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > MAP_HEIGHT:
            self.rect.bottom = MAP_HEIGHT

        direction = pygame.Vector2(player_rect.center) - pygame.Vector2(self.rect.center)

        # Поворот
        angle = math.degrees(-math.atan2(direction.y, direction.x)) + 90
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move_and_collide(self, dx, dy, obstacles):
        self.rect.x += int(dx)
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if dx > 0:
                    self.rect.right = obstacle.left
                elif dx < 0:
                    self.rect.left = obstacle.right

        self.rect.y += int(dy)
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if dy > 0:
                    self.rect.bottom = obstacle.top
                elif dy < 0:
                    self.rect.top = obstacle.bottom

        # Ограничи врага границами карты
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > MAP_WIDTH:
            self.rect.right = MAP_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > MAP_HEIGHT:
            self.rect.bottom = MAP_HEIGHT


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
