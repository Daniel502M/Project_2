import pygame
import math
from settings import BULLET_SPEED


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, target):
        super().__init__()
        # Загружаем базовое изображение пули
        base_image = pygame.image.load("assets/bullet.png").convert_alpha()

        # Направление
        direction = pygame.Vector2(target) - pygame.Vector2(pos)
        if direction.length() == 0:
            direction = pygame.Vector2(1, 0)
        self.velocity = direction.normalize() * BULLET_SPEED

        # Расчёт угла поворота (по оси Y вверх, по X — вправо)
        angle = math.degrees(math.atan2(-self.velocity.y, self.velocity.x))
        self.image = pygame.transform.rotate(base_image, angle)

        self.rect = self.image.get_rect(center=pos)
        self.spawn_time = pygame.time.get_ticks()

    def update(self, dt, bullet_blocking, enemies):
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt

        for ob in bullet_blocking:
            if ob.colliderect(self.rect):
                self.kill()
                return

        if pygame.time.get_ticks() - self.spawn_time > 3000:
            self.kill()
