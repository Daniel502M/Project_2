import pygame
import math
from settings import BULLET_SPEED


class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, target_pos):
        super().__init__()
        original_image = pygame.image.load('assets/bullet.png').convert_alpha()
        dx = target_pos[0] - pos[0]
        dy = target_pos[1] - pos[1]
        angle = math.atan2(dy, dx)
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * BULLET_SPEED
        self.image = pygame.transform.rotate(original_image, -math.degrees(angle))
        self.rect = self.image.get_rect(center=pos)
        self.spawn_time = pygame.time.get_ticks()

    def update(self, obstacles):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        # 💥 Проверка столкновения с препятствием
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                self.kill()  # Удаляем пулю при попадании в стену/дверь
                return

