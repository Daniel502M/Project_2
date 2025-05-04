import pygame
import math
from settings import BULLET_SPEED, WIDTH, HEIGHT


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, target_pos):
        super().__init__()
        self.image = pygame.image.load('assets/bullet.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        angle = math.atan2(target_pos[1] - pos[1], target_pos[0] - pos[0])
        self.velocity = pygame.math.Vector2(math.cos(angle) * BULLET_SPEED, math.sin(angle) * BULLET_SPEED)
        self.spawn_time = pygame.time.get_ticks()

    def update(self, obstacles):
        self.rect.center += self.velocity

        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                self.kill()
                return

