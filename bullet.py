import pygame
import math
from settings import BULLET_SPEED


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, target_pos):
        super().__init__()
        original_image = pygame.image.load('assets/bullet.png').convert_alpha()

        # Вычисляем угол от pos к target_pos (направление мышки)
        dx = target_pos[0] - pos[0]
        dy = target_pos[1] - pos[1]
        angle = math.atan2(dy, dx)

        # Направление движения (вперёд, в сторону выстрела)
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * BULLET_SPEED

        # Поворачиваем изображение в направлении движения
        self.image = pygame.transform.rotate(original_image, -math.degrees(angle))
        self.rect = self.image.get_rect(center=pos)

        self.spawn_time = pygame.time.get_ticks()

    def update(self, obstacles):
        self.rect.center += self.velocity

        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                self.kill()
                return
