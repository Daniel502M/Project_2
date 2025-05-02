import pygame
import math
from settings import PLAYER_SPEED
from bullet import Bullet
from settings import MAP_WIDTH, MAP_HEIGHT


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.original_image = pygame.image.load('assets/player.png').convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)
        self.collision_rect = pygame.Rect(
            self.rect.x + 10, self.rect.y + 10, self.rect.width - 20, self.rect.height - 20
        )
        self.speed = PLAYER_SPEED
        self.health = 100
        self.ammo = 20
        self.shooting = False
        self.shoot_cooldown = 250
        self.last_shot = pygame.time.get_ticks()
        self.reload_font = pygame.font.Font(None, 30)

        # ==== НАСТРАИВАЕМЫЙ ХИТБОКС ====
        self.hitbox_width = int(self.rect.width * 0.6)
        self.hitbox_height = int(self.rect.height * 0.8)
        self.hitbox = pygame.Rect(0, 0, self.hitbox_width, self.hitbox_height)
        self.update_hitbox()

    def update(self, keys, mouse_pos, bullets_group, obstacles):
        dx, dy = self.handle_movement(keys)
        self.rotate(mouse_pos)
        self.handle_shooting(mouse_pos, bullets_group)
        self.move_and_collide(dx, dy, obstacles)
        self.update_hitbox()
        self.collision_rect.topleft = self.rect.topleft

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def handle_movement(self, keys):
        dx = dy = 0
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed
        return dx, dy

    def rotate(self, mouse_pos):
        rel_x, rel_y = mouse_pos[0] - self.rect.centerx, mouse_pos[1] - self.rect.centery
        angle = math.degrees(-math.atan2(rel_y, rel_x)) + 282
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def handle_shooting(self, mouse_pos, bullets_group):
        now = pygame.time.get_ticks()
        if self.shooting and now - self.last_shot > self.shoot_cooldown and self.ammo > 0:
            bullet = Bullet(self.rect.center, mouse_pos)
            bullets_group.add(bullet)
            self.ammo -= 1
            self.last_shot = now

    def draw_reload_indicator(self, screen):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_cooldown:
            text = self.reload_font.render("Reloading...", True, (255, 0, 0))
            screen.blit(text, (10, 70))

    def draw_collision_rect(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.collision_rect, 2)

    def move_and_collide(self, dx, dy, obstacles):
        self.rect.x += dx
        self.update_hitbox()
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle):
                if dx > 0:
                    self.rect.right = obstacle.left
                elif dx < 0:
                    self.rect.left = obstacle.right
                self.update_hitbox()

        self.rect.y += dy
        self.update_hitbox()
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle):
                if dy > 0:
                    self.rect.bottom = obstacle.top
                elif dy < 0:
                    self.rect.top = obstacle.bottom
                self.update_hitbox()

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > MAP_WIDTH: self.rect.right = MAP_WIDTH
        if self.rect.top < 0: self.rect.top = 0
        if self.rect.bottom > MAP_HEIGHT: self.rect.bottom = MAP_HEIGHT
        self.update_hitbox()
