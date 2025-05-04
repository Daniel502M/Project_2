import pygame
import math
import random
from settings import ENEMY_SPEED, MAP_WIDTH, MAP_HEIGHT


class Enemy(pygame.sprite.Sprite):
    def __init__(self, target_pos):
        super().__init__()
        self.speed = ENEMY_SPEED
        self.health = 25
        self.alive = True
        self.state = "moving"
        self.current_frame = 0
        self.animation_speed = 0.07
        self.attack_damage_applied = False

        self.move_frames = [pygame.image.load(f"assets/Animation/Zombie_Brown_Animation_{i+1}.png").convert_alpha() for i in range(7)]
        self.attack_frames = [pygame.image.load(f"assets/Attack_Animation/Zombie_Brown_Attack_Animation_{i+1}.png").convert_alpha() for i in range(4)]
        self.death_frames = [pygame.image.load(f"assets/Zombie_Kill/Zombie_Brown_Kill_{i+1}.png").convert_alpha() for i in range(2)]

        self.image = self.move_frames[0]
        self.rect = self.image.get_rect(center=random_spawn_position())

        self.hitbox_width = int(self.rect.width * 0.3)
        self.hitbox_height = int(self.rect.height * 0.5)
        self.hitbox = pygame.Rect(0, 0, self.hitbox_width, self.hitbox_height)
        self.update_hitbox()

    def update(self, player, obstacles):
        if not self.alive:
            self.animate_death()
            return

        if self.can_damage(player.hitbox, obstacles):
            self.state = "attacking"
            self.animate_attack(player)
        else:
            collided = self.move_towards_player(player.hitbox, obstacles)
            self.state = "idle" if collided else "moving"

            if self.state == "moving":
                self.animate_movement()
            elif self.state == "idle":
                self.animate_idle()

    def can_damage(self, player_hitbox, obstacles):
        if not self.hitbox.colliderect(player_hitbox):
            return False

        start = self.hitbox.center
        end = player_hitbox.center

        for obstacle in obstacles:
            if obstacle.clipline(start, end):
                return False  # Между врагом и игроком есть препятствие

        return True  # Прямой путь к игроку без препятствий

    def move_towards_player(self, player_hitbox, obstacles):
        dx = player_hitbox.centerx - self.rect.centerx
        dy = player_hitbox.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            return False

        dx = dx / dist * self.speed
        dy = dy / dist * self.speed
        collided = False

        original_x = self.rect.x
        self.rect.x += dx
        self.update_hitbox()
        if any(self.hitbox.colliderect(ob) for ob in obstacles):
            self.rect.x = original_x
            self.update_hitbox()
            collided = True

        original_y = self.rect.y
        self.rect.y += dy
        self.update_hitbox()
        if any(self.hitbox.colliderect(ob) for ob in obstacles):
            self.rect.y = original_y
            self.update_hitbox()
            collided = True

        self.rect.clamp_ip(pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT))
        self.update_hitbox()

        direction = pygame.Vector2(player_hitbox.center) - pygame.Vector2(self.rect.center)
        angle = math.degrees(-math.atan2(direction.y, direction.x)) + 90
        self.image = pygame.transform.rotate(self.move_frames[int(self.current_frame)], angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        return collided

    def animate_attack(self, player):
        self.current_frame += self.animation_speed
        index = int(self.current_frame)

        if index < len(self.attack_frames):
            self.image = self.attack_frames[index]
            if index == 2 and not self.attack_damage_applied:
                self.attack_damage_applied = True
                player.take_damage(5)
        else:
            self.current_frame = 0
            self.attack_damage_applied = False

    def animate_movement(self):
        self.current_frame += self.animation_speed
        if self.current_frame >= len(self.move_frames):
            self.current_frame = 0
        self.image = self.move_frames[int(self.current_frame)]

    def animate_idle(self):
        self.image = self.move_frames[0]

    def animate_death(self):
        self.current_frame += self.animation_speed
        index = int(self.current_frame)
        if index < len(self.death_frames):
            self.image = self.death_frames[index]
        else:
            self.kill()

    def take_damage(self, amount):
        if self.alive:
            self.health -= amount
            if self.health <= 0:
                self.alive = False
                self.state = "dead"
                self.current_frame = 0

    def update_hitbox(self):
        self.hitbox.center = self.rect.center

    def draw_collision_rect(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.hitbox, 2)


def random_spawn_position():
    edge = random.choice(['top', 'bottom', 'left', 'right'])
    if edge == 'top':
        return random.randint(0, MAP_WIDTH), -60
    elif edge == 'bottom':
        return random.randint(0, MAP_WIDTH), MAP_HEIGHT + 60
    elif edge == 'left':
        return -60, random.randint(0, MAP_HEIGHT)
    else:
        return MAP_WIDTH + 60, random.randint(0, MAP_HEIGHT)
