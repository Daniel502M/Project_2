import pygame
import random


class Coin(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("assets/coin.png").convert_alpha()
        self.rect = self.image.get_rect(center=(
            pos[0] + random.randint(-10, 10),
            pos[1] + random.randint(-10, 10)
        ))

    def update(self):
        pass
