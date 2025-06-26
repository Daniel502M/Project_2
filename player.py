import pygame
import math
from settings import PLAYER_SPEED, MAP_WIDTH, MAP_HEIGHT


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.original_image = pygame.image.load('assets/player.png').convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=pos)

        self.speed = PLAYER_SPEED
        self.health = 100
        self.alive = True
        self.ammo = 20
        self.shooting = False
        self.shoot_cooldown = 250
        self.last_shot = pygame.time.get_ticks()
        self.reload_font = pygame.font.Font(None, 30)
        self.health_font = pygame.font.Font(None, 32)

        self.hitbox_width = int(self.rect.width * 0.35)
        self.hitbox_height = int(self.rect.height * 0.55)
        self.hitbox = pygame.Rect(0, 0, self.hitbox_width, self.hitbox_height)
        self.update_hitbox()

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        print(f"Игрок получил урон! Текущее здоровье: {self.health}")
        if self.health == 0:
            self.die()

    def die(self):
        self.alive = False
        print("Player has died!")

    def update(self, keys, mouse_pos, bullets_group, obstacles, shoot_sound=None):
        dx, dy = self.handle_movement(keys)
        self.rotate(mouse_pos)
        self.handle_shooting(mouse_pos, bullets_group, shoot_sound)
        self.move_and_collide(dx, dy, obstacles)
        self.update_hitbox()

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def draw_hitbox(self, screen, offset):
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox.move(-offset), 2)

    def draw_health(self, screen):
        color = (0, 255, 0) if self.health > 50 else (255, 255, 0) if self.health > 25 else (255, 0, 0)
        text = self.health_font.render(f"Health: {self.health}", True, color)
        screen.blit(text, (10, 10))

    def handle_movement(self, keys):
        dx = dy = 0
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed
        return dx, dy

    def rotate(self, mouse_pos):
        rel_x = mouse_pos[0] - self.rect.centerx
        rel_y = mouse_pos[1] - self.rect.centery
        angle = math.degrees(-math.atan2(rel_y, rel_x)) + 282
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def handle_shooting(self, mouse_pos, bullets_group, shoot_sound=None):
        now = pygame.time.get_ticks()
        if self.shooting and now - self.last_shot > self.shoot_cooldown and self.ammo > 0:
            from bullet import Bullet  # импорт внутри, чтобы избежать цикличности
            bullet = Bullet(self.rect.center, mouse_pos)
            bullets_group.add(bullet)
            self.ammo -= 1
            self.last_shot = now
            if shoot_sound:
                shoot_sound.play()

    def draw_reload_indicator(self, screen):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_cooldown:
            text = self.reload_font.render("Reloading...", True, (255, 0, 0))
            screen.blit(text, (10, 70))

    def move_and_collide(self, dx, dy, obstacles):
        self.hitbox.x += dx
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle):
                if dx > 0:
                    self.hitbox.right = obstacle.left
                elif dx < 0:
                    self.hitbox.left = obstacle.right

        self.hitbox.y += dy
        for obstacle in obstacles:
            if self.hitbox.colliderect(obstacle):
                if dy > 0:
                    self.hitbox.bottom = obstacle.top
                elif dy < 0:
                    self.hitbox.top = obstacle.bottom

        if self.hitbox.left < 0: self.hitbox.left = 0
        if self.hitbox.right > MAP_WIDTH: self.hitbox.right = MAP_WIDTH
        if self.hitbox.top < 0: self.hitbox.top = 0
        if self.hitbox.bottom > MAP_HEIGHT: self.hitbox.bottom = MAP_HEIGHT

        self.rect.center = self.hitbox.center
