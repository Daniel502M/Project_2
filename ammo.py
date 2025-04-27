import pygame
from settings import *


def spawn_ammo(pos, ammo_pickups):
    ammo_pickups.append({'pos': pos, 'amount': pickup_amount})


def draw_ammo_pickups(ammo_pickups, screen, camera_offset):
    for pickup in ammo_pickups:
        screen_x = int(pickup['pos'][0] - camera_offset[0])
        screen_y = int(pickup['pos'][1] - camera_offset[1])
        pygame.draw.circle(screen, (100, 100, 255), (screen_x, screen_y), pickup_radius)
