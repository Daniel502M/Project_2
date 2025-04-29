import pygame
import math
from settings import ENEMY_SPEED


class Enemy(pygame.sprite.Sprite):
    def __init__(self, target_pos):
        super().__init__()
        enemy_image_original = pygame.image.load("assets/enemy.png").convert_alpha()
        self.original_image = pygame.transform.scale(enemy_image_original, (60, 60))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(random_spawn_position()))
        self.speed = ENEMY_SPEED
        self.health = 50

    def update(self, player_rect):
        # Движение к игроку
        direction = pygame.Vector2(player_rect.center) - pygame.Vector2(self.rect.center)
        if direction.length() != 0:
            direction = direction.normalize()
            self.rect.center += direction * self.speed

        # Поворот в сторону игрока
        angle = math.degrees(-math.atan2(direction.y, direction.x)) + 90
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)


def random_spawn_position():
    import random
    # Спавним за краями экрана
    side = random.choice(['top', 'bottom', 'left', 'right'])
    if side == 'top':
        return (random.randint(0, 800), -50)
    elif side == 'bottom':
        return (random.randint(0, 800), 650)
    elif side == 'left':
        return (-50, random.randint(0, 600))
    else:
        return (850, random.randint(0, 600))
