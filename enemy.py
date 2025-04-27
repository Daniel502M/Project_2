import pygame
import random
import math
from settings import ENEMY_SPEED, SPAWN_DISTANCE, WIDTH, HEIGHT


class Enemy(pygame.sprite.Sprite):
    def __init__(self, player_pos):
        super().__init__()

        self.image = pygame.image.load('assets/enemy.png').convert_alpha()
        self.rect = self.image.get_rect()

        # Спавним за границей экрана
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.rect.center = (random.randint(0, WIDTH), -SPAWN_DISTANCE)
        elif side == 'bottom':
            self.rect.center = (random.randint(0, WIDTH), HEIGHT + SPAWN_DISTANCE)
        elif side == 'left':
            self.rect.center = (-SPAWN_DISTANCE, random.randint(0, HEIGHT))
        else:
            self.rect.center = (WIDTH + SPAWN_DISTANCE, random.randint(0, HEIGHT))

        self.speed = ENEMY_SPEED
        self.player_pos = player_pos
        self.health = 50

    def update(self, player_rect):
        # Бежим к игроку
        dir_vector = pygame.math.Vector2(player_rect.centerx - self.rect.centerx,
                                         player_rect.centery - self.rect.centery)
        if dir_vector.length() != 0:
            dir_vector = dir_vector.normalize()
        self.rect.centerx += dir_vector.x * self.speed
        self.rect.centery += dir_vector.y * self.speed
