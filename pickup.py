import pygame


class AmmoPickup(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load('assets/ammo_pickup.png').convert_alpha()
        self.rect = self.image.get_rect(center=pos)
